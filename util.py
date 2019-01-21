import time
import numpy as np

class FrequencyPrinter:
	def __init__(self, process_name, print_time=60):
		self.process_name = process_name
		self.print_time = print_time
		self.count = 0
		self.start_time = time.time()

	def tick(self):
		t = time.time()
		if t - self.start_time > self.print_time:
			print('[{}]\t{}hz'.format(self.process_name, float(self.count)/self.print_time))
			self.count = 0
			self.start_time = t
		else:
			self.count += 1


class CircularBuffer:
	''' circular buffer that can take variable amounts of data.
	most recent data at the back '''

	def __init__(self, size, dtype=np.int64):
		self.size = size
		self.index = 0
		self.array = np.zeros(self.size, dtype=dtype)

	def push(self, data):
		if data.size > 0:
			end = (self.index + data.size) % self.size
			if end > self.index:
				self.array[self.index:end] = data
			elif end == 0:
				self.array[self.index:] = data
			else:
				self.array[self.index:] = data[:-end]
				self.array[:end] = data[-end:]

			self.index = end


	def get(self):
		return np.concatenate([self.array[self.index:], self.array[:self.index]])


def test_circular_buffer():
	passed = True

	c = CircularBuffer(100)

	# empty array is empty
	answer = np.zeros(100, np.int64)
	passed &= (np.all(c.get() == answer))

	# adding 100 elements
	c.push(np.arange(100))
	answer = np.arange(100)
	passed &= (np.all(c.get() == answer))

	# adding a few elements
	c.push(np.arange(10))
	answer[:-10] = answer[10:]
	answer[-10:] = np.arange(10)
	passed &= (np.all(c.get() == answer))

	# adding one element
	c.push(np.array([100]))
	answer[:-1] = answer[1:]
	answer[-1] = 100
	passed &= (np.all(c.get() == answer))

	# adding elements that wrap around
	c = CircularBuffer(100)
	c.push(np.zeros(60))
	c.push(np.ones(60))
	answer = np.zeros(100)
	answer[40:] = np.ones(60)
	passed &= (np.all(c.get() == answer))

	return passed

if __name__ == '__main__':
	print 'CircularBuffer:\t', test_circular_buffer()
