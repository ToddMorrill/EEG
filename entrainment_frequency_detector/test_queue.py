import time
import Queue
from threading import Thread
import numpy as np
import os

"""
TODO: create a class so that global variables like tape and log file are treated better
"""

np.set_printoptions(2, suppress=True)

q = Queue.Queue()

# use to approximate the speed to the incoming EEG stream
sleeper = (1 - 0.15) / 256.
fft_size = 1024
tape = np.empty(fft_size)
step_size = int(fft_size * 0.05)

log_file = "test_queue_log.txt"
if os.path.isfile(log_file):
	os.remove(log_file)
	open(log_file, "w").close()
else:
	open(log_file, "w").close()

start = time.time()

def worker():
	counter = 0
	while True:
		if counter == 0:
			counter += 1
			for i in range(fft_size):
				tape[i] = q.get()
				#print(q.qsize())
			f = open(log_file, "a")
			f.write(str(tape))
			f.write("\n")
			f.close()
			# this is where we will call the fft function
			q.task_done()

		else:
			counter += 1
			tape[:-step_size] = tape[step_size:]
			for i in range(step_size):
				tape[-step_size+i:] = q.get()
				#print(q.qsize())
			f = open(log_file, "a")
			f.write(str(tape))
			f.write("\n")
			f.close()
			# this is where we will call the fft function
			q.task_done()

num_worker_threads = 1
for i in range(num_worker_threads):
     t = Thread(target=worker)
     t.daemon = True
     t.start()

# 5000 / 256 ~= 20 seconds to run
for i in range(5000):
	q.put(i)
	# this is where we will add the EEG signal to the queue
	#print(q.qsize())
	time.sleep(sleeper)

print(time.time() - start)
