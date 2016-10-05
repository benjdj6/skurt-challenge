import skurt_challenge
import unittest
import time

#Written by Ben Johnston (github: benjdj6)
#Last Edited: 5 Oct, 2016

class TestInsideRange(unittest.TestCase):
	
	#Tests that insideRange returns True when the position is set
	#on a horizontal boundary
	def testHorizontal(self):
		position = [2.0,0.0]
		polygon = [[0.0,0.0],[2.0,2.0],[4.0,0.0],[0.0,0.0]]
		self.assertTrue(skurt_challenge.insideRange(position,polygon))

	#Tests that insideRange returns True when the position is set
	#on a diagonal boundary
	def testDiagonal(self):
		position = [1.0,1.0]
		polygon = [[0.0,0.0],[2.0,2.0],[4.0,0.0],[0.0,0.0]]
		self.assertTrue(skurt_challenge.insideRange(position,polygon))

	#Tests that insideRange returns True when the position is set
	#on a vertical boundary
	def testVertical(self):
		position = [0.0, 1.0]
		polygon = [[0.0,0.0],[0.0,2.0],[4.0,0.0],[0.0,0.0]]
		self.assertTrue(skurt_challenge.insideRange(position,polygon))

	#Tests that insideRange returns False when the position is set
	#in the area of two intersecting squares
	def testWeirdShape(self):
		position = [1.5, 0.5]
		polygon = [[0.0,0.0],[0.0,2.0],[2.0,2.0],[2.0,1.0],[3.0,1.0],[3.0,-1.0],[1.0,-1.0],
		[1.0,0.0],[1.0,1.0],[2.0,1.0],[2.0,0.0],[1.0,0.0],[0.0,0.0]]
		self.assertFalse(skurt_challenge.insideRange(position,polygon))

	#Tests that insideRange returns True when the position is set
	#in the area
	def testInside(self):
		position = [2.0,1.0]
		polygon = [[0.0,0.0],[2.0,2.0],[4.0,0.0],[0.0,0.0]]
		self.assertTrue(skurt_challenge.insideRange(position,polygon))

	#Tests that insideRange returns False when the position is set
	#outside of the area
	def testOutside(self):
		position = [2.0, 3.0]
		polygon = [[0.0,0.0],[2.0,2.0],[4.0,0.0],[0.0,0.0]]
		self.assertFalse(skurt_challenge.insideRange(position,polygon))

	#Tests that insideRange returns True when the position is set
	#to a vertex
	def testAtVertex(self):
		position = [2.0, 2.0]
		polygon = [[0.0,0.0],[2.0,2.0],[4.0,0.0],[0.0,0.0]]
		self.assertTrue(skurt_challenge.insideRange(position,polygon))

	#Tests that insideRange returns False when the position is set
	#outside of a concave boundary
	def testInDent(self):
		position = [1.0, 1.0]
		polygon = [[0.0,0.0],[2.0,1.0],[0.0,2.0],[4.0,2.0],[3.0,0.0],[0.0,0.0]]
		self.assertFalse(skurt_challenge.insideRange(position,polygon))

class TestShouldSendEmail(unittest.TestCase):

	#Tests that shouldSendEmail returns True when in Quiet Mode
	#and the car isn't currently marked as out of bounds
	def testQuietModeCarIn(self):
		skurt_challenge.options.quietMode = True
		skurt_challenge.outCars = {}
		self.assertTrue(skurt_challenge.shouldSendEmail(1))

	#Tests that shouldSendEmail returns False when in Quiet Mode
	#and the car is already marked as out of bounds
	def testQuietModeCarOut(self):
		skurt_challenge.options.quietMode = True
		skurt_challenge.outCars[1] = 3.1415
		self.assertFalse(skurt_challenge.shouldSendEmail(1))

	#Tests that shouldSendEmail returns False when the car is marked
	#as out of bounds and a warning email for it was sent under 5 minutes ago
	def testCarOutUnder5(self):
		skurt_challenge.options.quietMode = False
		skurt_challenge.outCars[1] = time.time()
		self.assertFalse(skurt_challenge.shouldSendEmail(1))

	#Tests that shouldSendEmail returns True when the car is marked
	#as out of bounds and a warning email for it was sent over 5 minutes ago
	def testCarOutOver5(self):
		skurt_challenge.options.quietMode = False
		skurt_challenge.outCars[1] = time.time() - 300
		self.assertTrue(skurt_challenge.shouldSendEmail(1))

	#Tests that shouldSendEmail returns True when the car is not marked
	#as out of bounds yet
	def testCarIn(self):
		skurt_challenge.options.quietMode = False
		skurt_challenge.outCars = {}
		self.assertTrue(skurt_challenge.shouldSendEmail(1))

if __name__ == '__main__':
	unittest.main()


