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
sample_rate = 256
sleeper = (1 - 0.15) / float(sample_rate)
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

def max_freq(data):
    data = data * np.hanning(len(data)) # smooth the FFT by windowing data
    fft = abs(np.fft.fft(data).real)
    fft = fft[:int(len(fft)/2)] # keep only first half due to the nyquist frequency
    freq = np.fft.fftfreq(len(data),1/float(sample_rate))
    freq = freq[:int(len(freq)/2)] # keep only first half due to the nyquist frequency
    freq_peak = freq[np.where(fft==np.max(fft))[0][0]]
    print("peak frequency: %d Hz"%freq_peak)

def worker():
	counter = 0
	while True:
		if counter == 0:
			start_work = time.time()
			counter += 1
			for i in range(fft_size):
				tape[i] = q.get()
				#print(q.qsize())
			f = open(log_file, "a")
			f.write(str(tape))
			f.write("\n")
			f.close()
			max_freq(tape)
			print("fft time", time.time() - start_work)
			q.task_done()

		else:
			start_work = time.time()
			counter += 1
			tape[:-step_size] = tape[step_size:]
			for i in range(step_size):
				tape[-step_size+i:] = q.get()
				#print(q.qsize())
			f = open(log_file, "a")
			f.write(str(tape))
			f.write("\n")
			f.close()
			max_freq(tape)
			print("fft time", time.time() - start_work)
			q.task_done()

num_worker_threads = 1
for i in range(num_worker_threads):
     t = Thread(target=worker)
     t.daemon = True
     t.start()

# 5000 / 256 ~= 20 seconds to run
for i in range(5000):
	# toy code
	f = 10 # frequency
	y = np.sin(2 * np.pi * f * i / sample_rate)
	q.put(y)
	# this is where we will add the EEG signal to the queue
	# print(q.qsize())
	time.sleep(sleeper)

print(time.time() - start)
