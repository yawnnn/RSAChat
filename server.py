from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from rsa import *

def exchange_keys(conn):
	keys = conn.recv(BUFSIZ).decode('utf8')
	pub, n = keys.split(';')
	hosts_keys[conn] = (int(pub), int(n))
	msg = '{0};{1}'.format(cert[0], cert[2])
	conn.send(bytes(msg, 'utf8'))

def encrypt_msg(conn, msg):
	chiperText = encrypt(msg, hosts_keys[conn][0], hosts_keys[conn][1], 32)
	return ';'.join(str(b) for b in chiperText)

def decrypt_msg(conn, chiperText):
	blocks = []
	for block in chiperText.split(';'):
		blocks.append(int(block))
	msg = decrypt(blocks, cert[1], cert[2], 32)
	return msg

def accept_connections(socket):

	while True:
		conn, addr = socket.accept()
		clients[conn] = addr

		exchange_keys(conn)
		print('{0}:{1} has connected.'.format(addr[0], addr[1]))
		send(conn, 'Enter your name')

		Thread(target=handle_client, args=(conn,)).start()

def handle_client(conn):
	chiperText = conn.recv(BUFSIZ).decode('utf8')
	name = decrypt_msg(conn, chiperText)

	if name == 'q' or name == '':
		del clients[conn]
		conn.close()
		return
	broadcast('{0} joined the chat'.format(name))
	names[conn] = name

	try:
		while True:
			chiperText = conn.recv(BUFSIZ).decode('utf8')
			msg = decrypt_msg(conn, chiperText)

			if msg != 'q' and msg != '':
				broadcast('{0}: {1}'.format(name, msg))
			else:
				del clients[conn]
				broadcast('{0} left the chat'.format(name))
				conn.close()
				break
	except:
		socket.close()

def send(conn, msg):
	chiperText = encrypt_msg(conn, msg)
	conn.send(bytes(chiperText, 'utf8'))

def broadcast(msg):
	crashed = []

	for client in clients:
		try:
			chiperText = encrypt_msg(client, msg)
			client.send(bytes(chiperText, 'utf8'))
		except BrokenPipeError:
			crashed.append(client)

	for client in crashed:
		del clients[client]

	for client in crashed:
		broadcast('{0} left the chat'.format(names[client]))

ADDR = 'localhost'
PORT = 33000
BUFSIZ = 1024

clients = {}
names = {}
hosts_keys = {}
cert = genKeys()

socket = socket(AF_INET, SOCK_STREAM)

if __name__ == "__main__":

	socket.bind((ADDR, PORT))
	socket.listen(5)

	try:
		print("Waiting for connection...")
		accept_thread = Thread(target=accept_connections, args=(socket,))
		accept_thread.start()
		accept_thread.join()
	except:
		socket.close()

	socket.close()

