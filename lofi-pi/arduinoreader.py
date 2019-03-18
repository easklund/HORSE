import serial
import threading
import re
from time import sleep

class ArduinoReader(threading.Thread):
	_ADDR_BASE = "/dev/tty.usbserial-142"
	# _ADDR_BASE = "/dev/ttyUSB"

	def __init__(self):
		threading.Thread.__init__(self)
		self._mRun = False
		self._calibrated = False
		self._addressCounter = 0
		self._address = self._ADDR_BASE + str(self._addressCounter)
		self._hasSeenReading = False
		self._reading = None

	def run(self):
		self._mRun = True
		print("Arduino sensor reader started...")
		while self._mRun:
			try:
				print("Locating Arduino at " + self._address)
				ser = serial.Serial(self._address, 115200)
				while self._mRun:
					if (ser.in_waiting > 0):
						input = ser.readline()
						inputParsed = re.search("'(.*)'", str(input))
						inputParsed = inputParsed.group(1)[:-4]
						if inputParsed[:2] == "//": # Input is a comment
							print("Comment from Arduino: " + inputParsed[2:])
						else:
							self._reading = inputParsed
							self._hasSeenReading = False
			except serial.serialutil.SerialException:
				print("No device found at " + self._address)
				self._addressCounter += 1 if self._addressCounter < 10 else -10
				sleep(1)
				self._address = self._ADDR_BASE + str(self._addressCounter)

	def getReading(self):
		reading = None if self._hasSeenReading else self._reading
		self._hasSeenReading = True
		return reading

	def stop(self):
		self._mRun = False
