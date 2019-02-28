import socket
import random
import time
from sensorreader import SensorReader

TCP_IP = '0.0.0.0'
TCP_PORT = 5005
BUFFER_SIZE = 1024
connOpen = False

def main():
	global connOpen
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((TCP_IP, TCP_PORT))
	s.listen(1)
	sensor = SensorReader()
	sensor.start()

	try:
		while True:
			print("Server running, waiting a connection...")

			conn, addr = s.accept()
			connOpen = True
			print ('Connection address:', addr)

			while connOpen:
				try:
					if not sensor.isCalibrated():
						conn.send(("Calibrating sensor...\n").encode())
					else:
						reading = str(round(sensor.getReading(), 2))
						print("Sending: " + reading)
						conn.send((reading + "\n").encode())
					time.sleep(0.01)
					# data = conn.recv(BUFFER_SIZE)
					# if not data: break
					# print ("received data:", data)
				except (BrokenPipeError, ConnectionResetError):
					print("Connection closed")
					connOpen = False
	except KeyboardInterrupt:
		print("\nServer stopped")
		sensor.stop()
		if connOpen:
			conn.close()

if __name__ == "__main__":
    main()
