'''
        Read Gyro and Accelerometer by Interfacing Raspberry Pi with MPU6050 using Python
	http://www.electronicwings.com
'''
import smbus			#import SMBus module of I2C
from time import sleep          #import
from datetime import datetime
import threading
import math

class SensorReader(threading.Thread):
	#some MPU6050 Registers and their Address
	_PWR_MGMT_1   = 0x6B
	_SMPLRT_DIV   = 0x19
	_CONFIG       = 0x1A
	_GYRO_CONFIG  = 0x1B
	_INT_ENABLE   = 0x38
	_ACCEL_XOUT_H = 0x3B
	_ACCEL_YOUT_H = 0x3D
	_ACCEL_ZOUT_H = 0x3F
	_GYRO_XOUT_H  = 0x43
	_GYRO_YOUT_H  = 0x45
	_GYRO_ZOUT_H  = 0x47


	_DEVICE_ADDRESS = 0x68   # MPU6050 device address

	# Frequency of reading the sensor
	_FREQUENCY = 25 #in hz
	_REC_F = 1 / _FREQUENCY
	_F_CONST = 1 / (_FREQUENCY * 65.5)

	def __init__(self):
		threading.Thread.__init__(self)
		self._mRun = False
		self._calibrated = False
		self._reading = None
		self._gyro_x = 0
		self._gyro_y = 0
		self._gyro_z = 0
		self._acc_x = 0
		self._acc_y = 0
		self._acc_z = 0
		self._gyro_x_cal = 0
		self._gyro_y_cal = 0
		self._gyro_z_cal = 0
		self._bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards

	def run(self):
		print("Starting sensor")
		self._MPU_Init()
		self._mRun = True

		angle_pitch = 0
		angle_roll = 0
		set_gyro_angles = False
		angle_pitch_output = 0
		angle_roll_output = 0

		self._setupSensor()

		while (self._mRun):
			self._read_mpu_6050_data()
			self._gyro_x -= self._gyro_x_cal
			self._gyro_y -= self._gyro_y_cal
			self._gyro_z -= self._gyro_z_cal

			angle_pitch += self._gyro_x * self._F_CONST
			angle_pitch += self._gyro_y * self._F_CONST

			angle_pitch += angle_roll * math.sin(self._gyro_z * 0.000001066)
			angle_roll -= angle_pitch * math.sin(self._gyro_z * 0.000001066)

			acc_total_vector = math.sqrt((self._acc_x*self._acc_x)+(self._acc_y*self._acc_y)+(self._acc_z*self._acc_z))


			angle_pitch_acc = math.asin(self._acc_y/acc_total_vector)* 57.296
			angle_roll_acc = math.asin(self._acc_x/acc_total_vector)* -57.296

			if set_gyro_angles:
				angle_pitch = angle_pitch * 0.9996 + angle_pitch_acc * 0.0004
				angle_roll = angle_roll * 0.9996 + angle_roll_acc * 0.0004
			else:
				angle_pitch = angle_pitch_acc
				angle_roll = angle_roll_acc
				set_gyro_angles = True

			angle_pitch_output = angle_pitch_output * 0.9 + angle_pitch * 0.1
			angle_roll_output = angle_roll_output * 0.9 + angle_roll * 0.1
			self._reading = angle_pitch_output
			# print(self._reading)
			# print(" | Angle  = " + str(angle_pitch_output))

			# Wait until the time has passed, to keep the frequency
			while (datetime.now() - self._loop_timer).total_seconds() < (self._REC_F):
				pass
			self._loop_timer = datetime.now()
		print("Sensor stopped...")

	def getReading(self):
		return self._reading

	def isCalibrated(self):
		return self._calibrated

	def stop(self):
		self._mRun = False

	def _MPU_Init(self):
		#write to sample rate register
		self._bus.write_byte_data(self._DEVICE_ADDRESS, self._SMPLRT_DIV, 7)
		#Write to power management register
		self._bus.write_byte_data(self._DEVICE_ADDRESS, self._PWR_MGMT_1, 1)
		#Write to Configuration register
		self._bus.write_byte_data(self._DEVICE_ADDRESS, self._CONFIG, 0)
		#Write to Gyro configuration register
		self._bus.write_byte_data(self._DEVICE_ADDRESS, self._GYRO_CONFIG, 24)
		#Write to interrupt enable register
		self._bus.write_byte_data(self._DEVICE_ADDRESS, self._INT_ENABLE, 1)

	def _read_raw_data(self, addr):
		#Accelero and Gyro value are 16-bit
		high = self._bus.read_byte_data(self._DEVICE_ADDRESS, addr)
		low = self._bus.read_byte_data(self._DEVICE_ADDRESS, addr+1)

		#concatenate higher and lower value
		value = ((high << 8) | low)

		#to get signed value from mpu6050
		if(value > 32768):
			value = value - 65536
		return value

	def _read_mpu_6050_data(self):
		#Read Accelerometer raw value
		self._acc_x = self._read_raw_data(self._ACCEL_XOUT_H)
		self._acc_y = self._read_raw_data(self._ACCEL_YOUT_H)
		self._acc_z = self._read_raw_data(self._ACCEL_ZOUT_H)

		#Read Gyroscope raw value
		self._gyro_x = self._read_raw_data(self._GYRO_XOUT_H)
		self._gyro_y = self._read_raw_data(self._GYRO_YOUT_H)
		self._gyro_z = self._read_raw_data(self._GYRO_ZOUT_H)

	def _setupSensor(self):
		print("Calibrating sensor...")
		for i in range(1000):
			self._read_mpu_6050_data()
			self._gyro_x_cal += self._gyro_x
			self._gyro_y_cal += self._gyro_y
			self._gyro_z_cal += self._gyro_z
			sleep(0.003)

		self._gyro_x_cal /= 1000
		self._gyro_y_cal /= 1000
		self._gyro_z_cal /= 1000
		self._calibrated = True
		print("Sensor calibrated")
		self._loop_timer = datetime.now()
