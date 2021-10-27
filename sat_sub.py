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


# Read and parse config.ini
parser = SafeConfigParser()
parser.read('config.ini')
sat_port = parser.get('params', 'sat_port')
mo_time_interval = float(parser.get('params', 'mo_time'))
mt_time_interval = float(parser.get('params', 'mt_time'))
adc_status = -1
gpio = CDLL('./SC16IS752GPIO.so')
OUT = 1
IN  = 0
json_data = {"IMEI": 0, "ADC_status":-1, "GPIO_status":-1, "status_iridium": -1, "sampleMO":mo_time_interval, "sampleMT":mt_time_interval, "ADC1":0.0, "ADC2":0.0, "ADC3":0.0, "ADC4":0.0, "ADC5":0.0, "ADC6":0.0, "ADC7":0.0, "ADC8":0.0, "D1":0, "D2":0,"D3":0, "D4":0, "D5":0, "D6":0, "D7":0, "D8":0}
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


# RockBlock MO
class MoTPZ(rockBlockProtocol):
	def main(self):
		rb = rockBlock.rockBlock(sat_port, self)
		rb.sendMessage(string_data)
		rb.close()

	def rockBlockTxStarted(self):
		logger.info("rockBlockTxStarted")
		print ("rockBlockTxStarted")

	def rockBlockTxFailed(self):
		logger.warning("rockBlockTxFailed")
		print ("rockBlockTxFailed")

	def rockBlockTxSuccess(self, momsn):
		logger.info("rockBlockTxSuccess")
		print ("rockBlockTxSuccess " + str(momsn))


# RockBlock MT
class MtTPZ(rockBlockProtocol):
	def main(self):
		rb = rockBlock.rockBlock(sat_port, self)
		rb.messageCheck()
		rb.close()

	def rockBlockRxStarted(self):
		logger.info("rockBlockRxStarted")
		print "rockBlockRxStarted"

	def rockBlockRxFailed(self):
		logger.warning("rockBlockRxFailed")
		print "rockBlockRxFailed"

	def rockBlockRxReceived(self,mtmsn,data):
		logger.info("rockBlockRxReceived " + data)
		print "rockBlockRxReceived " + str(mtmsn) + " " + data
		cmd = json.loads(data)
		commandMT(cmd)

	def rockBlockRxMessageQueue(self,count):
		pass



# Command
def commandMT(cmd_json):
	global json_data, mo_time_interval, mt_time_interval, reset
	cmd_list_keys = list(cmd_json)
	cmd_list_values = list(cmd_json.values())

	# Update json data (DO values are read from sensors?)
	param = cmd_list_keys[0]
	value = cmd_list_values[0]

	# Check for reset command
	if param == "reset":
		os.system('reboot')

	# Check for digital output command
	elif param[0] == "D":
		value = min(value,1)
		pin = int(param[1]) -1
		gpio.SC16IS752GPIO_Write(pin, value)

	# Change for change sample time command (MO)
	elif param == "sampleMO":
		json_data[param] = value
		logger.info("Change MO sample time")
		parser.set('params', 'mo_time', str(value))
		with open('config.ini', 'wb') as configfile:
			parser.write(configfile)

	# Change for change sample time command (MT)
	elif param == "sampleMT":
		json_data[param] = value
		logger.info("Change MT sample time")
		parser.set('params', 'mt_time', str(value))
		with open('config.ini', 'wb') as configfile:
			parser.write(configfile)


# Check Iridium connection at boot
def iridium_init():
	global json_data
	while True:
		try:
			imei=confSBD().main()
			json_data["IMEI"] = imei
			json_data["status_iridium"] = 1
			update_state()
			break
		except:
			json_data["status_iridium"] = 0
			update_state()


# Init ADC
def adc_init():
	global json_data
	while True:
		adc_status = adc.init_adc()
		if adc_status:
			json_data["ADC_status"] = 1
			update_state()
			break
		else:
			json_data["ADC_status"] = 0
			update_state()


# Init I/O
def gpio_init():
	global json_data
	while True:
		try:
			gpio.SC16IS752GPIO_Init()
			for x in range(8):
				gpio.SC16IS752GPIO_Mode(x, OUT)
			json_data["GPIO_status"] = 1
			update_state()
			break
		except:
			json_data["GPIO_status"] = 0
			update_state()


# Iridium state
def iridium_state(state):
	global json_data
	json_data["status_iridium"] = state
	update_state()


# Sensor data
def sensor_data():
	global json_data

	# Read ADC
	try:
		values = adc.read_adc()
		json_data["ADC1"] = round(values[1], 2)
		json_data["ADC2"] = round(values[2], 2)
		json_data["ADC3"] = round(values[3], 2)
		json_data["ADC4"] = round(values[4], 2)
		json_data["ADC5"] = round(values[5], 2)
		json_data["ADC6"] = round(values[6], 2)
		json_data["ADC7"] = round(values[7], 2)
		json_data["ADC8"] = round(values[8], 2)
		json_data["ADC_status"] = 1
	except:
		json_data["ADC_status"] = 0
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
		json_data["GPIO_status"] = 1
	except:
		json_data["GPIO_status"] = 0
		logger.warning("GPIO bad status")

	update_state()



# Update state string
def update_state():
	global string_data
	string_data = json.dumps(json_data, sort_keys=True)
	logger.info(string_data)


# BOX thread
def box_thread():
	iridium_init() 	                # init Iridium
	adc_init()			# init ADC
	gpio_init()			# init GPIO

	tStartMO = tStartMT = time.time()		# timer
	while True:

		# Check for MT
		now = time.time()
		elapsed_time_MT = int(abs(now-tStartMT))
		if(elapsed_time_MT >= mt_time_interval):
			try:
				MtTPZ().main()                  # check MT
				iridium_state(1)
			except:
				logger.error("Iridium not connected")
				iridium_state(0)
			tStartMT = time.time()                  # restart timer after MT check

		# Update values and send MO
		now = time.time()
		elapsed_time_MO = int(abs(now-tStartMO))
		if(elapsed_time_MO >= mo_time_interval):
			try:
				MoTPZ().main()                  # send MO
				iridium_state(1)
			except:
				logger.error("Iridium not connected")
				iridium_state(0)
			tStartMO = time.time()                  # restart timer after MO is sent

		# Update sensor data
		sensor_data()

		# Sleep
		time.sleep(2)



# API Class Box
class Box(Resource):
	def get(self):
		return json_data, 200

	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('parameter', type=str, required=True)
		parser.add_argument('value', type=int, required=True)
		args = parser.parse_args()
		param = args.parameter
		value = args.value
		command = {param: value}
		commandMT(command)
		return {}, 200



# Start main thread
if __name__ == '__main__':

	# Start box thread
	boxThread = threading.Thread(target=box_thread)
	boxThread.daemon = True
	boxThread.start()

	# Define REST API
	app = Flask(__name__)
	api = Api(app)
	cors = CORS(app)
	api.add_resource(Box, '/box')
	log = logging.getLogger('werkzeug')
	log.disabled = True
	app.run(host='0.0.0.0', port=5000)

