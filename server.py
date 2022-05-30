import threading
from time import sleep
from socket import socket as _socket, AF_INET, SOCK_STREAM
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
	while not stop.is_set():
		conn, addr = socket.accept()
		clients[conn] = addr

		exchange_keys(conn)
		print('%s:%s has connected.' % (addr[0], addr[1]))
		send(conn, 'Enter your name')

		threading.Thread(target=handle_client, args=(conn,addr,)).start()

def handle_client(conn, addr):
	# there is one thread running this loop for each client connected

	signedText = conn.recv(BUFSIZ).decode('utf8')
	if signedText == 'q':
		del clients[conn]
		conn.close()
		print('%s:%s disconnected.' % (addr[0], addr[1]))
		return

	name = decrypt_msg(conn, signedText)
	broadcast('{0} joined the chat'.format(name))
	names[conn] = name

	while not stop.is_set():
		signedText = conn.recv(BUFSIZ).decode('utf8')
		if signedText == 'q':
			del clients[conn]
			broadcast('{0} left the chat'.format(name))
			print('%s:%s disconnected.' % (addr[0], addr[1]))
			conn.close()
			return

		msg = decrypt_msg(conn, signedText)
		broadcast('{0}: {1}'.format(name, msg))

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

def close_handler(signal, frame):
	socket.close()
	exit(0)

ADDR = 'localhost'
PORT = 33000
BUFSIZ = 1024
BLOCKSIZE = 16

# mapping socket and address
clients = {}
# mapping socket and chat name
names = {}
hosts_keys = {}
socket = None
stop = None
cert = None

if __name__ == "__main__":
	cert = RSA()
	stop = threading.Event()

	with _socket(AF_INET, SOCK_STREAM) as socket:
		socket.bind((ADDR, PORT))
		socket.listen(5)

		print("Waiting for connection...")
		accept_thread = threading.Thread(target=accept_connections, args=(socket,))
		accept_thread.start()
		
		try:
			while accept_thread.is_alive():
				sleep(1)
		except KeyboardInterrupt:
			stop.set()
			socket.close()


