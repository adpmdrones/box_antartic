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
from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import random
import adc


# Read and parse config.ini
parser = SafeConfigParser()
parser.read('config.ini')
sat_port = parser.get('params', 'sat_port')
mo_time_interval = float(parser.get('params', 'mo_time'))
mt_time_interval = float(parser.get('params', 'mt_time'))
box_id = parser.get('params', 'box_id')
json_data = {"BOXID":box_id, "sampleMO":mo_time_interval, "sampleMT":mt_time_interval, "ADC1":0.0, "ADC2":0.0, "ADC3":0.0, "ADC4":0.0, "ADC5":0.0, "ADC6":0.0, "ADC7":0.0, "ADC8":0.0, "D1":0, "D2":0,"D3":0, "D4":0, "D5":0, "D6":0, "D7":0, "D8":0}
string_data = json.dumps(json_data)
ir_status = 0
reset = 0


# Create logger
logger = logging.getLogger('ANTARTIC')
logging.basicConfig(level=logging.INFO, filename='/var/log/TPZANT/ant.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
logger.info("START")


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
		reset = 1
	else:
		json_data[param] = value

	# Check for digital output command
	if param[0] == "D":
		pass
		#setPin(command, value)

	# Change for change sample time command (MO)
	if param == "sampleMO":
		logger.info("Change MO sample time")
		parser.set('params', 'mo_time', str(value))
		with open('config.ini', 'wb') as configfile:
			parser.write(configfile)

	# Change for change sample time command (MT)
	if param == "sampleMT":
		logger.info("Change MT sample time")
		parser.set('params', 'mt_time', str(value))
		with open('config.ini', 'wb') as configfile:
			parser.write(configfile)



# Sensor data
def sensor_data():
	global json_data, string_data
	values = adc.read_adc()
	json_data["ADC1"] = values[1]
	json_data["ADC2"] = values[2]
	json_data["ADC3"] = values[3]
	json_data["ADC4"] = values[4]
	json_data["ADC5"] = values[5]
	json_data["ADC6"] = values[6]
	json_data["ADC7"] = values[7]
	json_data["ADC8"] = values[8]
	#json_data["DX"] = random.randint(0, 1)

	string_data = json.dumps(json_data, sort_keys=True)
	logger.info(string_data)


def box_thread():
	global ir_status
	tStartMO = time.time() - mo_time_interval	# force 1st MO (and sensor read)
	tStartMT = time.time() - mt_time_interval	# force 1st MT
	while True:

		# Reset
		if reset:
			time.sleep(1)
			os.system('reboot')

		# Check for MT
		now = time.time()
		elapsed_time_MT = int(abs(now-tStartMT))
		if(elapsed_time_MT >= mt_time_interval):
			try:
				MtTPZ().main()                  # check MT
				ir_status = 1
			except:
				logger.error("Iridium not connected")
				ir_status = 0
			tStartMT = time.time()                  # restart timer after MT check

		# Update values and send MO
		now = time.time()
		elapsed_time_MO = int(abs(now-tStartMO))
		if(elapsed_time_MO >= mo_time_interval):
			sensor_data()                           # read sensor data
			try:
				MoTPZ().main()                  # send MO
				ir_status = 1
			except:
				logger.error("Iridium not connected")
				ir_status = 0
			tStartMO = time.time()                  # restart timer after MO is sent

		# Sleep interval
		time.sleep(1)



# API Class Box
class Box(Resource):
	def get(self):
		json_data["status_iridium"] = ir_status
		return {"boxdata" : json_data}, 200


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

