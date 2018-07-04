import random

def refactor(m):
	# returns (s, d) such that m = (2 ** s) * d
	# m in binary is composed by powers of 2
	# so we find the smallest one by finding the
	# first 0b1 and by shifting m to the exp of 2 
	# corresponding to that 0b1 we get d

	assert m >= 0

	i = 0
	while m & (2 ** i) == 0:
		i += 1

	return (i, m >> i)



def isPrime(n, tries):
	#millerRabin primality test
	#time complexity of O(k * log^3 n)
	#the chance that the algorithm fails is of 4 ** tries

	s, d = refactor(n - 1)

	assert d % 2 != 0
	assert 2 ** s * d == n - 1

	def isComposite(a):
		x = pow(a, d, n)

		if x == 1 or x == n - 1:
			return True

		for _ in range(1, s - 1):
			x = pow(x, 2, n)

			if x == 1:
				return False
			if x == n - 1:
				return True
		return False

	for _ in range(tries):
		a = random.randint(2, n - 2)

		if not isComposite(a):
			return False
	return True

if __name__ == "__main__":

	n = random.randint(10**100, 10**101)

	print(isPrime(n, 50))
