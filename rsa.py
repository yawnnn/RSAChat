import random
import math
import primeTest
from hashlib import sha256

class RSA:

	def __init__(self, pub=None, n=None):
		if pub:
			self.pub = pub
			self.n = n
		else:
			self.pub, self.priv, self.n = self.genKeys()

	def getPubKey(self):
		return (self.pub, self.n)

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

	def string2intBlocks(self, string, blockSize):
		# returns the integer representation of the string
		# in blocks of blockSize bytes

		intBlocks = []

		def string2int(string):
			# string will be tranformed in the concatenation
			# of the ascii value of every letter in binary

			integer = 0

			for char in string:
				integer = (integer << 8) + ord(char)

			return integer

		# divide the string in chunks of 8 characterss
		chunks = [string[i:i+blockSize] for i in range(0, len(string), blockSize)]

		for substring in chunks:
			intBlocks.append(string2int(substring))

		if not len(string) & blockSize:
			intBlocks[-1] <<= 8 * (blockSize - (len(string) % blockSize))

		return intBlocks

	def intBlocks2string(self, intBlocks, blockSize):
		# converts a list of integers into a string
		# every 8 bits is a letter

		string = ''

		def int2asciiList(integer):
			# splits int in ascii values of every letter

			asciiList = []

			for i in range(blockSize):
				asciiList.append(integer & 255)
				integer >>= 8

			asciiList.reverse()
			
			return asciiList

		for block in intBlocks:
			asciiList = int2asciiList(block)

			for charValue in asciiList:
				string += chr(charValue)

		return string.replace('\x00', '')

	def encrypt(self, msg, key, blockSize):
		chiperText = []

		msgBlocks = self.string2intBlocks(msg, blockSize)

		for block in msgBlocks:
			chiperText.append(pow(block, key, self.n))

		return chiperText

	def decrypt(self, chiperText, key, blockSize):
		msgBlocks = []

		for block in chiperText:
			msgBlocks.append(pow(block, key, self.n))

		msg = self.intBlocks2string(msgBlocks, blockSize)

		return msg

	# hash is always long 64 hex characters
	def signMsg(self, msg):
		msgHash = sha256(bytes(msg, 'utf8')).hexdigest();
		signature = self.encrypt(msgHash, self.priv, 64)

		return self.concat(signature)

	def unsignMsg(self, signature):
		msgHash = self.decrypt([int(signature)], self.pub, 64)

		return msgHash

	def encryptMsg(self, msg, blockSize):
		chiperText = self.encrypt(msg, self.pub, blockSize)
		
		return self.concat(chiperText)

	def decryptMsg(self, chiperText, blockSize):
		msg = self.decrypt(self.deconcat(chiperText), self.priv, blockSize)

		return msg

	def concat(self, intBlocks):
		return ';'.join(str(b) for b in intBlocks)

	def deconcat(self, string):
		blocks = []

		for block in string.split(';'):
			blocks.append(int(block))

		return blocks

if __name__ == "__main__":
	
	message = "this is a test message"
	blockSize = 8

	cert = RSA()

	# sender
	chiperText = cert.encryptMsg(message, blockSize)
	signature = cert.signMsg(message)
	signedText = chiperText + chr(0) + signature

	#receiver
	ct, sig = signedText.split(chr(0))
	endMessage = cert.decryptMsg(ct, blockSize)
	msgHash = cert.unsignMsg(sig)

	if sha256(bytes(endMessage, 'utf8')).hexdigest() == msgHash:
		print('Signature confirmed')

	print('Received message: %s' % endMessage)
	