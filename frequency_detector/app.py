import eventlet 
eventlet.monkey_patch() # attempts to make everything greenlet friendly so that nothing blocks the websocket thread

from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

import pyaudio
import numpy as np

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = "eventlet"#None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

def max_freq():
    """"""
    #np.set_printoptions(suppress=True) # don't use scientific notation

    chunk = 4096*2 # number of data points to read at a time
    rate = 44100 # time resolution of the recording device (Hz)
    visualize = False
    
    p=pyaudio.PyAudio() # start the PyAudio class

    stream=p.open(format=pyaudio.paInt16,channels=2,rate=rate,input=True,
                  frames_per_buffer=chunk) #uses default input device

    while True: # run this until the user hits the stop button
        data = np.fromstring(stream.read(chunk),dtype=np.int16)
        data = data * np.hanning(len(data)) # smooth the FFT by windowing data
        fft = abs(np.fft.fft(data).real)
        fft = fft[:int(len(fft)/2)] # keep only first half due to the nyquist frequency
        freq = np.fft.fftfreq(chunk,1/float(rate))
        freq = freq[:int(len(freq)/2)] # keep only first half due to the nyquist frequency
        try:
            freq_peak = freq[np.where(fft==np.max(fft))[0][0]]+1
            print("peak frequency: %d Hz"%freq_peak)
        except:
            print("increase chunksize")
        if freq_peak > 300 and freq_peak < 350:
            socketio.emit('my_message', {'data': "300<freq<350 hz: up"})
        elif freq_peak > 350 and freq_peak < 400:
            socketio.emit('my_message', {'data': "350<freq<400 hz: down"})
        elif freq_peak > 400 and freq_peak < 450:
            socketio.emit('my_message', {'data': "400<freq<450 hz: left"})
        elif freq_peak > 450 and freq_peak < 500:
            socketio.emit('my_message', {'data': "450<freq<500 hz: right"})
        else:
            socketio.emit('my_message', {'data': str(int(freq_peak))+" hz"})
        socketio.sleep() # this frees up the cpu to to do other things, like listen for the stop command!

        @socketio.on('stop_event') # really nice thing about this is that this is only listening within the max_freq function
        # in other words, if the user clicks the stop button with no stream going, nothing happens!
        def stream_end(message):
            if message['data'] == 'stop':
                stream.stop_stream()
                stream.close()
                p.terminate()
                thread_lock.release()
                global thread
                thread = None
                print("stream stopped, thread free")

@socketio.on('start_event')
def stream_results(message):
    if message['data'] == 'start':
        global thread
        with thread_lock:
            if thread is None:
                thread = socketio.start_background_task(target=max_freq) # this thread may broadcast info to all sessions
                print("stream started on background thread")

# could revisit this functionality later
# @socketio.on('disconnect_request')
# def disconnect_request():
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_message',
#          {'data': 'Disconnected!', 'count': session['receive_count']})
#     disconnect()

# keep a running measure of latency
@socketio.on('my_ping')
def ping_pong():
    emit('my_pong')
    socketio.sleep()

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=False)
