import os
import random

N = 128
M = 30
b = 32
MAGIC = 0xb249b015
mask = (1 << b) - 1 # 0b111111...111 x32

class Twister:
	def rol(self, x, d):
		ans = (x << d) & mask # The & mask here just makes it 32 bit.
							  # First, left-shift d bits
		ans = ans | (x >> (b - d)) # Then, standard "OR" operator, rightshift 32 minus d bits
		return ans & mask # The & mask here just makes it 32 bit
		# Essentially, it left shifts it D amount, but it keeps the value of those bits by right shifting the same amount and ORing them
		# Here's an example:
		# 0b10010010 rol 3
		# First:
		# 0b10010010000 mod 8 = 0b10010000
		# Second:
		# 0b10010000 OR 0b00000100 = 
		# 0b10010100
		# The 100 from the left was wrapped around to the right. But this is 32 bit

	def __init__(self, state=None):
		self.index = N # self.index = 128
		if state is not None:
			assert len(state) == N # we can set the state of the randomizer by calling it. Could be important to solving
			self.STATE = state[:]
		else:
			self.STATE = [0] * N # [0 0 0 0 ... 0 ] x128
			for i in range(N):
				self.STATE[i] = int(os.urandom(4).encode('hex'), 16) # [random 32 bit values]
			for i in range(N):
				self.STATE[i] ^= random.getrandbits(32) # Bitwise XOR

			# Note - random.getrandbits() uses the Mersenne Twister PRNG, which is NOT cryptographically secure... 
			# and the class name is twister. However, os.urandom() IS cryptographically secure, so for all 
			# intents and purposes, N is self.STATE is random for the initial state

	def twist(self):
		for i in range(N):
			self.STATE[i] ^= self.rol(self.STATE[(i+1) % N], 3) # state[i] = state[i] XOR rol(state[i+1] % 128, 3)
			self.STATE[i] ^= self.rol(self.STATE[(i+M) % N], b - 9) # state[i] = state[i] XOR rol(state[i - 2] % 128, 23)
			self.STATE[i] ^= MAGIC # state[i] = state[i] XOR 0xb249b015

	def rand(self):
		if self.index >= N: # the first calling of rand() by number = random.rand() % 32 in the other script
							# triggers this, because self.index was set to 128 in the initializer
			self.twist()
			self.index = 0
		y = self.STATE[self.index] # y = state[index]
		y ^= self.rol(y, 7) # y = y XOR rol(y, 7)
		y ^= self.rol(y, b - 15) # y = y XOR rol(y, 17)
		self.index += 1 # Move on to next index

		return y & mask # return 32 bits of y, in theory &mask shouldn't matter here. Probably just a safety thing
						# The lower 5 bits of this are what we see in the roulette function.

	###
	# GOAL: Determine the entirety of self.STATE, 5 bits at a time, from a few thousand requests
	### 
	# PSEUDOCODE
	#
	# a = STATE[index]
	# index++
	# b = a XOR rol(a, 7)
	# c = b XOR rol(b, 17)
	# return c
