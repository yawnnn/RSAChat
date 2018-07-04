from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from chat import Chat
from rsa import *

def encrypt_msg(conn, msg):
	chiperText = encrypt(msg, server_keys[0], server_keys[1], 32)
	return ';'.join(str(b) for b in chiperText)

def decrypt_msg(conn, chiperText):
	blocks = []
	for block in chiperText.split(';'):
		blocks.append(int(block))
	msg = decrypt(blocks, cert[1], cert[2], 32)
	return msg

def exchange_keys():
	msg = '{0};{1}'.format(cert[0], cert[2])
	socket.send(bytes(msg, 'utf8'))
	keys = socket.recv(BUFSIZ).decode('utf8')
	pub, n = keys.split(';')
	server_keys.extend([int(pub), int(n)])

def receive():
	while True:
		try:
			chiperText = socket.recv(BUFSIZ).decode('utf8')
			msg = decrypt_msg(socket, chiperText)
			if msg != '':
				chat.showMessage(msg)

			else:
				break
		except OSError:  # Possibly client has left the chat.
			break

def send(event=None):
	msg = chat.getMessage()
	chiperText = encrypt_msg(socket, msg)
	socket.send(bytes(chiperText, 'utf8'))

	if msg == 'q':
		chat.close()

def on_close():
	socket.close()

ADDR = 'localhost'
PORT = 33000
BUFSIZ = 1024

socket = socket(AF_INET, SOCK_STREAM)
chat = Chat()
cert = genKeys()
server_keys = []

if __name__ == "__main__":

	socket.connect((ADDR, PORT))
	exchange_keys()
	recv_thread = Thread(target=receive)
	recv_thread.start()
	chat.start(send, on_close)


