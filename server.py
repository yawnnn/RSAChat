from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from hashlib import sha256
from rsa import RSA

def exchange_keys(conn):
	# at the beginning of the communication each other's
	# public key and n get sent to the other

	keys = conn.recv(BUFSIZ).decode('utf8')
	pub, n = keys.split(';')
	hosts_keys[conn] = RSA(int(pub), int(n))
	msg = '%s;%s' % cert.getPubKey()
	conn.send(bytes(msg, 'utf8'))

def encrypt_msg(conn, msg):
	chiperText = hosts_keys[conn].encryptMsg(msg, BLOCKSIZE)
	signature = cert.signMsg(msg)

	return chiperText + chr(0) + signature

def decrypt_msg(conn, signedText):
	chiperText, signature = signedText.split(chr(0))
	msg = cert.decryptMsg(chiperText, BLOCKSIZE)
	msgHash = hosts_keys[conn].unsignMsg(signature)

	if msgHash == sha256(bytes(msg, 'utf8')).hexdigest():
		return msg
	else:
		raise ValueError("signature doesn't match")

def accept_connections(socket):
	while True:
		conn, addr = socket.accept()
		clients[conn] = addr

		exchange_keys(conn)
		print('%s:%s has connected.' % (addr[0], addr[1]))
		send(conn, 'Enter your name')

		Thread(target=handle_client, args=(conn,)).start()

def handle_client(conn):
	# there is one thread running this loop for each client connected

	signedText = conn.recv(BUFSIZ).decode('utf8')
	name = decrypt_msg(conn, signedText)

	if name == 'q' or name == '':
		del clients[conn]
		conn.close()
		return
	broadcast('{0} joined the chat'.format(name))
	names[conn] = name

	try:
		while True:
			signedText = conn.recv(BUFSIZ).decode('utf8')
			msg = decrypt_msg(conn, signedText)

			if msg != 'q' and msg != '':
				broadcast('{0}: {1}'.format(name, msg))
			else:
				del clients[conn]
				broadcast('{0} left the chat'.format(name))
				conn.close()
				break
	except:
		# Exceptions from here won't be catched in main's try-catch
		socket.close()

def send(conn, msg):
	signedText = encrypt_msg(conn, msg)
	conn.send(bytes(signedText, 'utf8'))

def broadcast(msg):
	# every message will be sent to everyone in the chat

	crashed = []

	for client in clients:
		try:
			signedText = encrypt_msg(client, msg)
			client.send(bytes(signedText, 'utf8'))
		except BrokenPipeError:
			crashed.append(client)

	for client in crashed:
		del clients[client]

	for client in crashed:
		broadcast('%s left the chat' % names[client])

ADDR = 'localhost'
PORT = 33000
BUFSIZ = 1024
BLOCKSIZE = 16

# mapping socket and address
clients = {}
# mapping socket and chat name
names = {}
hosts_keys = {}
cert = RSA()

if __name__ == "__main__":
	with socket(AF_INET, SOCK_STREAM) as s:
		socket.bind((ADDR, PORT))
		socket.listen(5)

		print("Waiting for connection...")
		accept_thread = Thread(target=accept_connections, args=(socket,))
		accept_thread.start()
		accept_thread.join()

