import socket
import random
import time

TCP_IP = '0.0.0.0'
TCP_PORT = 5005
BUFFER_SIZE = 1024
connOpen = False

def main():
    global connOpen
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)

    try:
        while True:
            print("Server running, waiting a connection...")

            conn, addr = s.accept()
            connOpen = True
            print ('Connection address:', addr)

            while connOpen:
                try:
                    randNum = "{:.1f}".format(random.uniform(0, 90)) + "°"
                    print("Sending " + randNum);
                    conn.send((randNum + "\n").encode())
                    time.sleep(1)
                    # data = conn.recv(BUFFER_SIZE)
                    # if not data: break
                    # print ("received data:", data)
                except BrokenPipeError:
                    print("Connection closed")
                    connOpen = False
    except KeyboardInterrupt:
        print("\nStop")
        if connOpen:
            conn.close()

if __name__ == "__main__":
    main()
