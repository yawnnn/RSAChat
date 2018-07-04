from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from rsa import RSA

def exchange_keys(conn):
	keys = conn.recv(BUFSIZ).decode('utf8')
	pub, n = keys.split(';')
	hosts_keys[conn] = RSA(int(pub), int(n))
	msg = '%s;%s' % cert.getPubKey()
	conn.send(bytes(msg, 'utf8'))

# These two functions just handle format problems
# found it was better to be handled here rather than
# in the RSA class itself
def encrypt_msg(conn, msg):
	chiperText = hosts_keys[conn].encrypt(msg, 32)
	return ';'.join(str(b) for b in chiperText)

def decrypt_msg(conn, chiperText):
	blocks = []
	for block in chiperText.split(';'):
		blocks.append(int(block))
	msg = cert.decrypt(blocks, 32)
	return msg

def accept_connections(socket):

	while True:
		conn, addr = socket.accept()
		clients[conn] = addr

		exchange_keys(conn)
		print('%s:%s has connected.' % (addr[0], addr[1]))
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
		# Exceptions from here won't be catched in main's try
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
		broadcast('%s left the chat' % names[client])

ADDR = 'localhost'
PORT = 33000
BUFSIZ = 1024

clients = {}
names = {}
hosts_keys = {}
cert = RSA()

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
		# Only needed to close the socket no matter what,
		# since otherwise you won't be able to open another one 
		# once you restart the program
		socket.close()

	socket.close()

