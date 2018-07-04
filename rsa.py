import random
import math
import primeTest
from hashlib import sha256

class RSA:

	def __init__(self, e=None, n=None):
		if e:
			self.e = e
			self.n = n
		else:
			self.e, self.d, self.n = self.genKeys()

	def getPubKey(self):
		return (self.e, self.n)

	def getRandom(self, start, end):
			x = random.randint(start, end)
			
			if x % 2 == 0:
				x += 1

			return x

	def findPrime(self, start, end, tries):
		x = self.getRandom(start, end)

		while True:
			if primeTest.isPrime(x, tries):
				return x
			else:
				x = self.getRandom(start, end)

	def modularInverse(self, a, m):
		# euclid extended algorithm, look it up to 
		# understand what's going on here
		# the format is [(r, s, t)]
		seq = [(m, 1, 0), (a, 0, 1)]

		while True:
			quotient = seq[-2][0] // seq[-1][0]
			seq.append((seq[-2][0] - (quotient * seq[-1][0]),
						seq[-2][1] - (quotient * seq[-1][1]),
						seq[-2][2] - (quotient * seq[-1][2])))

			if seq[-1][0] == 0:
				del seq[-1]
				break

		return seq[-1][2]

	def genKeys(self, start=10**100, end=10**104, tries=50):

		modifier = random.choice([0.01, 0.1])

		p = self.findPrime(start, end, tries)
		q = self.findPrime(start, end, tries)

		n = p * q
		totientN = (p-1) * (q-1)
		d = 0

		while True:
			d = self.findPrime(max(p, q), totientN, tries)

			if math.gcd(d, totientN) == 1:
				break

		e = self.modularInverse(d, totientN)

		# returning e % totientN prevents e from being negative
		# without corrupting the key
		return (e % totientN, d, n)

	def string2asciiList(self, string):
		asciiList = []
		
		for char in string:
			asciiList.append(ord(char))

		return asciiList

	def asciiList2string(self, asciiList):
		string = ""

		for asciiChar in asciiList:
			string += chr(asciiChar)

		return string.replace('\x00', '')

	def asciiList2intBlocks(self, asciiList, length):
		blocks = []

		if len(asciiList) % length != 0:
			for i in range(length - len(asciiList) % length):
				asciiList.append(0)

		for i in range(0, len(asciiList), length):
			integer = 0b0

			for j in range(length):
				integer += asciiList[i + j] * pow(256, length - j - 1)

			blocks.append(integer)

		return blocks

	def intBlocks2asciiList(self, blocks, length):
	    asciiList = []

	    for integer in blocks:
	        inner = []

	        for i in range(length):
	            inner.append(integer % 256)
	            integer >>= 8

	        inner.reverse()
	        asciiList.extend(inner)

	    return asciiList

	# hash is always long 64 hex characters
	def signMsg(self, msg, blockSize=64):
		msgHash = sha256(msg);
		return msgHash.hexdigest()

	def encrypt(self, msg, blockSize):
		chiperText = []

		asciiMsg = self.string2asciiList(msg)
		msgBlocks = self.asciiList2intBlocks(asciiMsg, blockSize)

		for block in msgBlocks:
			chiperText.append(pow(block, self.e, self.n))

		return chiperText

	def decrypt(self, chiperText, blockSize):
		msgBlocks = []

		for block in chiperText:
			msgBlocks.append(pow(block, self.d, self.n))

		asciiMsg = self.intBlocks2asciiList(msgBlocks, blockSize)
		msg = self.asciiList2string(asciiMsg)

		return msg

	# def encryptMsg(self, msg, blockSize):


	# def decryptMsg(self, chiperText, blockSize):



if __name__ == "__main__":

	msg = 'hello baby'
	sha = sha256(bytes(msg, 'utf8'))
	print(sha.hexdigest())
	
	# message = "this is a test message"

	# cert = RSA()
	# print('e = ', cert.e, '\n')
	# print('d = ', cert.d, '\n')
	# print('n = ', cert.n, '\n')


	# chiperText = cert.encrypt(message, 32)
	# endMessage = cert.decrypt(chiperText, 32)

	# print('original msg: ', message, '\n')
	# print('chipertext: ', chiperText, '\n')
	# print('decrypted msg:', endMessage)
	


