def modular_pow(base, exp, mod):
	# Right-to-left binary method 
	# we use the binary form of exp => exp = sum(a_i * 2^i)
	# so b^e % n = prod(b^(a_i * 2^i)) % n
	# so we shift exp to get the next bit
	# and if it's 1 then we update result
	
	if mod == 1:
		return 0

	result = 1
	base = base % mod

	while exp > 0:
		if (exp % 2 == 1):
			result = (result * base) % mod
		exp = exp >> 1
		base = (base * base) % mod
	
	return result