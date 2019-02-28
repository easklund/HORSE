import time
from sensorreader import SensorReader

if __name__ == "__main__":
	sensor = SensorReader()
	sensor.start()
	try:
		while not sensor.isCalibrated():
			time.sleep(1)
		while True:
			print(sensor.getReading())
			time.sleep(0.05)
	except KeyboardInterrupt:
		sensor.stop()

	# sensor.stop()
