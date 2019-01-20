import time

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