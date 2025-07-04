
import socket

HOST = "127.0.0.1"
PORT = 6240

def main():

	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	client.connect((HOST, PORT))

	client.sendall(b"Hello mf")

	data = client.recv(1024)

	if data:
		print(data.decode())

	client.close()

main()