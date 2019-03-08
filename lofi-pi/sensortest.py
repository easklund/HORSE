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
			reading = sensor.getReading()
			if reading is not None:
				print(reading)
			time.sleep(0.01)
	except KeyboardInterrupt:
		sensor.stop()

	# sensor.stop()
