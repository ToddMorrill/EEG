# pseudo code

read file into Pandas DF

create a queue

counter = 0
fft_size = 1024
tape = np.array(1024 readings * 16 channels)
step size = 1024 * 0.05 ~= 51
while true:
	if counter = 0:
		data = grab the oldest 1024 values from the queue
		tape = data
		fft(tape)
		socketio.sleep()
	data = grab the oldest step size (1024*.05)51 values from the queue
	tape[:-step_size] = tape[step_size:] # shift data over
	tape[-size:] = data # set new values
	fft(tape)
	socketio.sleep()

def fft(tape):
	spectrum = np.fft.fft(tape) / fft_size
	freqs = np.fft.fftfreqs(fft_size)

	preds = {9:False, 10:False, 12:False}
	preds[9] = signal_detected(spectrum, freqs, freq_dict, hz=9)
	preds[10] = signal_detected(spectrum, freqs, freq_dict, hz=10)
	preds[12] = signal_detected(spectrum, freqs, freq_dict, hz=12)

	for key in preds:
		if pred[key]:
			socketio.emit(key)

