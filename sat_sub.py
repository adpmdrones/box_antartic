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
import random


# Read and parse config.ini
parser = SafeConfigParser()
parser.read('config.ini')
sat_port = parser.get('params', 'sat_port')
mo_time_interval = float(parser.get('params', 'mo_time'))
mt_time_interval = float(parser.get('params', 'mt_time'))
box_id = parser.get('params', 'box_id')
json_data = {"BOXID":box_id, "sampleMO":mo_time_interval, "sampleMT":mt_time_interval, "ADC1":10.33, "ADC2":45.78, "ADC3":22.19, "ADC4":93.23, "ADC5":18.45, "ADC6":39.53, "ADC7":67.69, "ADC8":11.554, "D1":1, "D2":1,"D3":0, "D4":1, "D5":0, "D6":0, "D7":0, "D8":1}
string_data = json.dumps(json_data)


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
		logger.info("TxStarted")
		print ("TxStarted")

	def rockBlockTxFailed(self):
		logger.warning("TxFailed")
		print ("TxFailed")

	def rockBlockTxSuccess(self, momsn):
		logger.info("TxSuccess")
		print ("TxSuccess " + str(momsn))


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
		logger.info("rockBlockRxReceived " + str(mtmsn) + " " + data)
		print "rockBlockRxReceived " + str(mtmsn) + " " + data
		commandMT(data)

	def rockBlockRxMessageQueue(self,count):
		#logger.info("rockBlockRxMessageQueue " + str(count))
		#print "rockBlockRxMessageQueue " + str(count)
		pass


# Command to DO
def commandMT(cmd):
	global json_data, mo_time_interval, mt_time_interval
	cmd_json = json.loads(cmd)
	cmd_list_keys = list(cmd_json)
	cmd_list_values = list(cmd_json.values())

	# Update json data (DO values are read from sensors?)
	for x in range(len(cmd_json)):
		try:
			index = cmd_list_keys[x]
			value = cmd_list_values[x]
			json_data[index] = value
		except:
			logger.warning("Bad command")
			print("Bad command")

	# Send command to digital outputs (if in cmd)


	# Change sample time (if in cmd)
	if mo_time_interval==json_data["sampleMO"]:
		pass
	else:
		logger.info("Change MO sample time")
		print("Change MO sample time")
		mo_time_interval = json_data["sampleMO"]
		parser.set('params', 'mo_time', str(mo_time_interval))
		with open('config.ini', 'wb') as configfile:
			parser.write(configfile)

	if mt_time_interval==json_data["sampleMT"]:
		pass
	else:
		logger.info("Change MT sample time")
		print("Change MT sample time")
		mt_time_interval = json_data["sampleMT"]
		parser.set('params', 'mt_time', str(mt_time_interval))
		with open('config.ini', 'wb') as configfile:
			parser.write(configfile)



# Sensor data
def sensor_data():
	global json_data, string_data
	json_data["ADC1"] = round(random.uniform(10.5, 15.5),2)		# random values for test
	json_data["ADC2"] = round(random.uniform(20.5, 25.5),2)		# random values for test
	json_data["ADC3"] = round(random.uniform(30.5, 35.5),2)		# random values for test
	json_data["ADC4"] = round(random.uniform(10.5, 15.5),2)		# random values for test
	json_data["ADC5"] = round(random.uniform(40.5, 43.5),2)		# random values for test
	json_data["ADC6"] = round(random.uniform(70.5, 75.5),2)		# random values for test
	json_data["ADC7"] = round(random.uniform(90.5, 95.5),2)		# random values for test
	json_data["ADC8"] = round(random.uniform(10.5, 25.5),2)		# random values for test
	#json_data["D1"] = random.randint(0, 1)
	#json_data["D2"] = random.randint(0, 1)
	#json_data["D3"] = random.randint(0, 1)
	#json_data["D4"] = random.randint(0, 1)
	#json_data["D5"] = random.randint(0, 1)
	#json_data["D6"] = random.randint(0, 1)
	#json_data["D7"] = random.randint(0, 1)
	#json_data["D8"] = random.randint(0, 1)

	string_data = json.dumps(json_data, sort_keys=True)
	logger.info(string_data)
	print(string_data)


# Start main thread
if __name__ == '__main__':
	tStart = time.time()
	while True:
		# Receive MT
		MtTPZ().main()

		# Check elapsed time
		now = time.time()
		elapsed_time = int(abs(now-tStart))

		# Update values and send MO
		if(elapsed_time > mo_time_interval):
			sensor_data()		# read sensor data
			MoTPZ().main()		# send MO
			tStart = time.time()	# restart timer after MO is sent

		# Sleep MT interval
		time.sleep(mt_time_interval)
