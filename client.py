from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from chat import Chat
from rsa import *

def encrypt_msg(conn, msg):
	chiperText = server_cert.encryptMsg(msg, BLOCKSIZE)
	signature = cert.signMsg(msg)

	return chiperText + chr(0) + signature

def decrypt_msg(conn, signedText):
	chiperText, signature = signedText.split(chr(0))
	msg = cert.decryptMsg(chiperText, BLOCKSIZE)
	msgHash = server_cert.unsignMsg(signature)

	if msgHash == sha256(bytes(msg, 'utf8')).hexdigest():
		return msg
	else:
		raise ValueError("signature doesn't match")

def exchange_keys():
	msg = '%s;%s' % cert.getPubKey()
	socket.send(bytes(msg, 'utf8'))
	keys = socket.recv(BUFSIZ).decode('utf8')
	pub, n = keys.split(';')
	global server_cert
	server_cert = RSA(int(pub), int(n))

def receive():
	while True:
		try:
			signedText = socket.recv(BUFSIZ).decode('utf8')
			msg = decrypt_msg(socket, signedText)
			if msg != '':
				chat.showMessage(msg)

			else:
				break
		except OSError:
			break

def send(event=None):
	msg = chat.getMessage()
	signedText = encrypt_msg(socket, msg)
	socket.send(bytes(signedText, 'utf8'))

	if msg == 'q':
		chat.close()

def on_close():
	socket.close()

ADDR = 'localhost'
PORT = 33000
BUFSIZ = 1024
BLOCKSIZE = 16

socket = socket(AF_INET, SOCK_STREAM)
chat = Chat()
cert = RSA()
server_cert = None

if __name__ == "__main__":

	socket.connect((ADDR, PORT))
	exchange_keys()
	recv_thread = Thread(target=receive)
	recv_thread.start()
	chat.start(send, on_close)


