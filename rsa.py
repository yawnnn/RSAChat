import random
import math
import primeTest
from hashlib import sha1

def hashMsg(msg):
	msgHash = sha1(msg);
	return msgHash.hexdigest()

def getRandom(start, end):
		x = random.randint(start, end)
		
		if x % 2 == 0:
			x += 1

		return x

def findPrime(start, end, tries):
	x = getRandom(start, end)

	while True:
		if primeTest.isPrime(x, tries):
			return x
		else:
			x = getRandom(start, end)

def modularInverse(a, m):
	# euclid extended algorithm, look it up to 
	# understand what's going on here
	# format (r, s, t)
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

def genKeys(start=10**100, end=10**104, tries=50):

	modifier = random.choice([0.01, 0.1])

	p = findPrime(start, end, tries)
	q = findPrime(start, end, tries)

	n = p * q
	totientN = (p-1) * (q-1)
	d = 0

	while True:
		d = findPrime(max(p, q), totientN, tries)

		if math.gcd(d, totientN) == 1:
			break

	e = modularInverse(d, totientN)

	# returning e % totientN prevents e from being negative
	# without corrupting the key
	return (e % totientN, d, n)

def string2asciiList(string):
	asciiList = []
	
	for char in string:
		asciiList.append(ord(char))

	return asciiList

def asciiList2string(asciiList):
	string = ""

	for asciiChar in asciiList:
		string += chr(asciiChar)

	return string.replace('\x00', '')

def asciiList2intBlocks(asciiList, length):
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

def intBlocks2asciiList(blocks, length):
    asciiList = []

    for integer in blocks:
        inner = []

        for i in range(length):
            inner.append(integer % 256)
            integer >>= 8

        inner.reverse()
        asciiList.extend(inner)

    return asciiList

def encrypt(message, e, n, blockSize):
	chiperText = []

	asciiMessage = string2asciiList(message)
	messageBlocks = asciiList2intBlocks(asciiMessage, blockSize)

	for block in messageBlocks:
		chiperText.append(pow(block, e, n))

	return chiperText

def decrypt(chiperText, d, n, blockSize):
	messageBlocks = []

	for block in chiperText:
		messageBlocks.append(pow(block, d, n))

	asciiMessage = intBlocks2asciiList(messageBlocks, blockSize)
	message = asciiList2string(asciiMessage)

	return message

if __name__ == "__main__":
	
	message = "questo e' un messaggio di test"

	e, d, n = genKeys()
	print('e = ', e, '\n')
	print('d = ', d, '\n')
	print('n = ', n, '\n')


	chiperText = encrypt(message, e, n, 32)
	endMessage = decrypt(chiperText, d, n, 32)

	print('messaggio originale: ', message, '\n')
	print('messaggio cifrato: ', chiperText, '\n')
	print('messaggio che legge infine il destinatario:', endMessage)
	


