#!/usr/bin/env python
"""
ADPM Drones Srl
https://www.adpmdrones.com
mailto:info@adpmdrones.com
"""

from ConfigParser import SafeConfigParser
import logging
import rockBlock as rockBlock
from rockBlock import rockBlockProtocol
import json
import time
import os
import threading
from ctypes import *
from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import serial
import adc
from gpiozero import CPUTemperature
import psutil
import copy


# Read and parse config.ini
parser = SafeConfigParser()
parser.read('config.ini')
sat_port = parser.get('params', 'sat_port')
mo_time_interval = int(parser.get('params', 'mo_time'))
max_time = int(parser.get('params', 'max_time'))
multip = float(parser.get('params', 'multip'))
forceMO = False
initSensors = False
gpio = CDLL('./SC16IS752GPIO.so')
OUT = 1
IN  = 0
json_data = {"IMEI": 0, "xA": multip, "ADC":-1, "GPIO":-1, "status_iridium": -1, "MO":mo_time_interval, "CPU": 0, "DFS": "100", "A1":0.0, "A2":0.0, "A3":0.0, "A4":0.0, "A5":0.0, "A6":0.0, "A7":0.0, "A8":0.0, "D1":0, "D2":0,"D3":0, "D4":0, "D5":0, "D6":0, "D7":0, "D8":0}
string_data = json.dumps(json_data)


# Create logger
logger = logging.getLogger('ANTARTIC')
logging.basicConfig(level=logging.INFO, filename='/var/log/TPZANT/ant.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
logger.info("START")


# Rockblock config
class confSBD(rockBlockProtocol):
        def main(self):
                rb = rockBlock.rockBlock(sat_port, self)
		return rb.getSerialIdentifier()


# RockBlock MO and MT
class SatTPZ(rockBlockProtocol):
	def main(self):
		rb = rockBlock.rockBlock(sat_port, self)
		rb.sendMessage(string_data)
		rb.close()

	def rockBlockTxStarted(self):
		logger.info("rockBlockMOStarted")
		print ("rockBlockMOStarted")

	def rockBlockTxFailed(self):
		logger.warning("rockBlockMOFailed")
		print ("rockBlockMOFailed")

	def rockBlockTxSuccess(self, momsn):
		logger.info("rockBlockMOSuccess")
		print ("rockBlockMOSuccess " + str(momsn))

	def rockBlockRxReceived(self,mtmsn,data):
		global forceMO
		logger.info("rockBlockMTReceived " + data)
		print "rockBlockMTReceived " + str(mtmsn) + " " + data
		try:
			forceMO = True
			split_data = data.split("=")
			key = split_data[0]
			value = split_data[1]
			cmd = {key:value}
			commandMT(cmd)
		except:
			logger.error("Bad provided command")

        def rockBlockRxMessageQueue(self,count):
                pass


# RockBlock MO
class MoTPZ(rockBlockProtocol):
	def main(self):
		rb = rockBlock.rockBlock(sat_port, self)
		rb.sendMessage(string_data)
		rb.close()

	def rockBlockTxStarted(self):
		logger.info("rockBlockMOStarted")
		print ("rockBlockMOStarted")

	def rockBlockTxFailed(self):
		logger.warning("rockBlockMOFailed")
		print ("rockBlockMOFailed")

	def rockBlockTxSuccess(self, momsn):
		logger.info("rockBlockMOSuccess")
		print ("rockBlockMOSuccess " + str(momsn))


# RockBlock MT
class MtTPZ(rockBlockProtocol):
	def main(self):
		rb = rockBlock.rockBlock(sat_port, self)
		rb.messageCheck()
		rb.close()

	def rockBlockRxStarted(self):
		logger.info("rockBlockMTStarted")
		print "rockBlockMTStarted"

	def rockBlockRxFailed(self):
		logger.warning("rockBlockMTFailed")
		print "rockBlockMTFailed"

	def rockBlockRxReceived(self,mtmsn,data):
		logger.info("rockBlockMTReceived " + data)
		print "rockBlockMTReceived " + str(mtmsn) + " " + data
		cmd = json.loads(data)
		commandMT(cmd)

	def rockBlockRxMessageQueue(self,count):
		pass



# Command
def commandMT(cmd_json, rest=0):
	global json_data, mo_time_interval, mt_time_interval, multip
	cmd_list_keys = list(cmd_json)
	cmd_list_values = list(cmd_json.values())

	# Update json data (DO values are read from sensors?)
	param = cmd_list_keys[0].upper()
	value = cmd_list_values[0]
	logger.info("CMD: " + str(param) + ", Value: " + str(value))

	# Check for reset command
	if param == "RESET":
		os.system('reboot')

	# Check for shutdown command (ONLY VIA REST)
	if param == "SHUTDOWN" and rest:
		os.system('sudo shutdown now')

	# Check for digital output command
	elif param[0] == "D":
		value = min(int(value),1)
		pin = int(param[1]) -1
		gpio.SC16IS752GPIO_Write(pin, value)

	# Change for change sample time command (MO)
	elif param == "SAMPLEMO":
		value = max(min(int(value), max_time), 10)	# saturate within 10 - max_time
		mo_time_interval = int(value)
		json_data["MO"] = value
		logger.info("Change MO sample time")
		parser.set('params', 'mo_time', str(value))
		with open('config.ini', 'wb') as configfile:
			parser.write(configfile)
		parser.set('params', 'mt_time', str(value))
		with open('config.ini', 'wb') as configfile:
			parser.write(configfile)

	# Change for change sample time command (MT)
	elif param == "MULTIP":
		value = float(max(min(value, 10.0), -10.0))	# saturate within -10 - 10
		multip = value
		json_data["xA"] = value
		logger.info("Change voltage factor")
		parser.set('params', 'multip', str(value))
		with open('config.ini', 'wb') as configfile:
			parser.write(configfile)

	# Command has no effect
	else:
		logger.warning("Command has no effect")



# Check Iridium connection at boot
def iridium_init():
	global json_data
	while True:
		try:
			imei = confSBD().main()
			json_data["IMEI"] = imei
			json_data["status_iridium"] = 1
			break
		except:
			json_data["status_iridium"] = 0


# Init ADC
def adc_init():
	global json_data
	while True:
		adc_status = adc.init_adc()
		if adc_status:
			json_data["ADC"] = 1
			break
		else:
			json_data["ADC"] = 0


# Init I/O
def gpio_init():
	global json_data
	while True:
		try:
			gpio.SC16IS752GPIO_Init()
			for x in range(8):
				gpio.SC16IS752GPIO_Mode(x, OUT)
				gpio.SC16IS752GPIO_Write(x, 0)
			json_data["GPIO"] = 1
			break
		except:
			json_data["GPIO"] = 0


# Iridium state
def iridium_state(state):
	global json_data
	json_data["status_iridium"] = state


# Sensor data
def sensor_data():
	global json_data

	# Read ADC
	try:
		values = adc.read_adc()
		json_data["A1"] = round(values[1] * multip, 2)
		json_data["A2"] = round(values[2] * multip, 2)
		json_data["A3"] = round(values[3] * multip, 2)
		json_data["A4"] = round(values[4] * multip, 2)
		json_data["A5"] = round(values[5] * multip, 2)
		json_data["A6"] = round(values[6] * multip, 2)
		json_data["A7"] = round(values[7] * multip, 2)
		json_data["A8"] = round(values[8] * multip, 2)
		json_data["ADC"] = 1
	except:
		json_data["ADC"] = 0
		logger.warning("ADC bad status")

	# Read I/O state
	try:
		json_data["D1"] = gpio.SC16IS752GPIO_Read(0)
		json_data["D2"] = gpio.SC16IS752GPIO_Read(1)
		json_data["D3"] = gpio.SC16IS752GPIO_Read(2)
		json_data["D4"] = gpio.SC16IS752GPIO_Read(3)
		json_data["D5"] = gpio.SC16IS752GPIO_Read(4)
		json_data["D6"] = gpio.SC16IS752GPIO_Read(5)
		json_data["D7"] = gpio.SC16IS752GPIO_Read(6)
		json_data["D8"] = gpio.SC16IS752GPIO_Read(7)
		json_data["GPIO"] = 1
	except:
		json_data["GPIO"] = 0
		logger.warning("GPIO bad status")


	# Read CPU and SD state
	try:
		cpu = CPUTemperature().temperature

		hdd = psutil.disk_usage('/')
                total = float(hdd.total / (2**30))
                used = float(hdd.used / (2**30))
                free = float(hdd.free / (2**30))
		freePerc = float((free/total))*100.0

		json_data["DFS"] = int(freePerc)
		json_data["CPU"] = cpu
	except:
		logger.warning("BOX bad internal status")




# Update state string
def update_state():
	global string_data

	# Make a copy of json state, in order to manage data to send via Iridium without modifying json state
	iridium_json = copy.copy(json_data)
	del iridium_json["status_iridium"]
	### manage data ###

	string_data = json.dumps(iridium_json, sort_keys=True)
	logger.info(string_data)


# BOX thread
def box_thread():
	global forceMO, initSensors
	iridium_init() 	                # init Iridium
	adc_init()			# init ADC
	gpio_init()			# init GPIO
	initSensors = True

	tStartMO = tStartMT = time.time()		# timer
	while True:

		# Update values and send MO
		now = time.time()
		elapsed_time_MO = int(abs(now-tStartMO))
		if(elapsed_time_MO >= mo_time_interval or forceMO):
			if forceMO:
				time.sleep(5)		# allow sensor values to be updated
				forceMO = False

			try:
				update_state()
				SatTPZ().main()                  # send MO and check for MT
				iridium_state(1)
			except:
				logger.error("Iridium not connected")
				iridium_state(0)

			tStartMO = time.time()                   # restart timer

		time.sleep(2)


# Sensors thread
def sensors_thread():
	while initSensors == False:
		time.sleep(2)
		pass
	while True:
		sensor_data()
		time.sleep(3)



# API Class Box
class Box(Resource):
	def get(self):
		return json_data, 200

	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('parameter', type=str, required=True)
		parser.add_argument('value', type=float, required=True)
		args = parser.parse_args()
		param = args.parameter
		value = args.value
		command = {param: value}
		commandMT(command, rest=1)
		return {}, 200



# Start main thread
if __name__ == '__main__':

	# Start box thread
	boxThread = threading.Thread(target=box_thread)
	boxThread.daemon = True
	boxThread.start()

	# Start sensors thread
        sensThread = threading.Thread(target=sensors_thread)
        sensThread.daemon = True
        sensThread.start()

	# Define REST API
	app = Flask(__name__)
	api = Api(app)
	cors = CORS(app)
	api.add_resource(Box, '/box')
	log = logging.getLogger('werkzeug')
	log.disabled = True
	app.run(host='0.0.0.0', port=5000)

