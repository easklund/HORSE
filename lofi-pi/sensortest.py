import time
from sensorreader import SensorReader
from arduinoreader import ArduinoReader

if __name__ == "__main__":
	sensor = ArduinoReader()
	sensor.start()
	try:
##		while not sensor.isCalibrated():
##			time.sleep(1)
		while True:
			print(sensor.getReading())
			time.sleep(2)
	except KeyboardInterrupt:
		sensor.stop()

	# sensor.stop()
