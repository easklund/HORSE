'''
        Read Gyro and Accelerometer by Interfacing Raspberry Pi with MPU6050 using Python
	http://www.electronicwings.com
'''
import smbus			#import SMBus module of I2C
from time import sleep          #import
from statistics import mean
from collections import deque
import matplotlib.pyplot as plt

#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47

def MPU_Init():
	#write to sample rate register
	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)

	#Write to power management register
	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)

	#Write to Configuration register
	bus.write_byte_data(Device_Address, CONFIG, 0)

	#Write to Gyro configuration register
	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)

	#Write to interrupt enable register
	bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
	#Accelero and Gyro value are 16-bit
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)

        #concatenate higher and lower value
        value = ((high << 8) | low)

        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value


bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68   # MPU6050 device address

MPU_Init()

window_top_start = 100
window_bottom_start = -100

fig = plt.figure()
ax = fig.add_subplot(111)
ax2 = fig.add_subplot(111)
ax3 = fig.add_subplot(111)
ax.grid(True, which='both')
ax.axvline(x=0, color='k')
fig.show()

print (" Reading Data of Gyroscope and Accelerometer")
gxs = deque()
moving_average_queue = deque()
moving_average = deque()
moving_average_diff = deque()
moving_average_queue_size = 10
xs = deque()
xs2 = deque()
counter = 0
window_size = 200
redraw_after_n_readings = 30
while True:

	#Read Accelerometer raw value
	acc_x = read_raw_data(ACCEL_XOUT_H)
	acc_y = read_raw_data(ACCEL_YOUT_H)
	acc_z = read_raw_data(ACCEL_ZOUT_H)

	#Read Gyroscope raw value
	gyro_x = read_raw_data(GYRO_XOUT_H)
	gyro_y = read_raw_data(GYRO_YOUT_H)
	gyro_z = read_raw_data(GYRO_ZOUT_H)

	#Full scale range +/- 250 degree/C as per sensitivity scale factor
	Ax = acc_x/16384.0
	Ay = acc_y/16384.0
	Az = acc_z/16384.0

	Gx = gyro_x/131.0
	Gy = gyro_y/131.0
	Gz = gyro_z/131.0

	gxs.append(Gx)
	xs.append(counter)
	
	if len(gxs) > window_size:
		gxs.popleft()
		xs.popleft()
		moving_average_diff.popleft()
	if len(moving_average) > window_size:
		moving_average.popleft()
		xs2.popleft()
	moving_average_queue.append(Gx)
	if len(moving_average) > 2:
		moving_average_diff.append(mean(moving_average_queue) - moving_average[len(moving_average) - 2])
	else:
		moving_average_diff.append(0)
	if len(moving_average_queue) > moving_average_queue_size:
		moving_average_queue.popleft()
		moving_average.append(mean(moving_average_queue))
		xs2.append(counter)
	if (counter % redraw_after_n_readings) == 0:
		window_top = window_top_start
		window_bottom = window_bottom_start
		for vals in range(max(0,len(gxs) - window_size), len(gxs)):
			window_top = max(window_top, gxs[vals])
			window_bottom = min(window_bottom, gxs[vals])
		ax.plot(xs, gxs, color='b')
		#ax.legend((gxs), ("text"))
		ax2.plot(xs2, moving_average, color='r')
		ax3.plot(xs, moving_average_diff, color='g')
		#plt.legend()
		plt.title("Sensor readings")
		fig.canvas.draw()
		ax.set_xlim(left=max(0, counter-window_size), right=counter+1)
		ax2.set_xlim(left=max(0, counter-window_size), right=counter+1)
		ax3.set_xlim(left=max(0, counter-window_size), right=counter+1)
		ax.set_ylim(bottom=window_bottom, top=window_top)
		ax2.set_ylim(bottom=window_bottom, top=window_top)
		ax3.set_ylim(bottom=window_bottom, top=window_top)
	counter += 1
	sleep(0.01)


#	print ("Gx=%.2f" %Gx, u'\u00b0'+ "/s", "\tGy=%.2f" %Gy, u'\u00b0'+ "/s", "\tGz=%.2f" %Gz, u'\u00b0'+ "/s", "\tAx=%.2f g" %Ax, "\tAy=%.2f g" %Ay, "\tAz=%.2f g" %Az)
