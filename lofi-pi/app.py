import socket

TCP_IP = '0.0.0.0'
TCP_PORT = 5005
BUFFER_SIZE = 1024

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)

    conn, addr = s.accept()
    print ('Connection address:', addr)
    try:
        while True:
            conn.send(input().encode())
            # data = conn.recv(BUFFER_SIZE)
            # if not data: break
            # print ("received data:", data)
    except KeyboardInterrupt:
        print("\nStop")
    conn.close()

if __name__ == "__main__":
    main()
