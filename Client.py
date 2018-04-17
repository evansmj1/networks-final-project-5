import cv2
import numpy as np
import time
import pyaudio
import socket
import wave
import pickle
import json

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("connecting to localhost")
client_socket.connect(('localhost', 8080))

wf = wave.open("Man's Not Hot.wav")
p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

try:

    data = client_socket.recv(1024)

    while data:
        #print("receiving data")
        data = client_socket.recv(500000)

        #print(data.decode('utf-8'))
        #data = json.loads(data.decode('utf-8'))
        #audio = client_socket.recv(500000)


        nparr = np.fromstring(data, np.uint8)


        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)


        if type(frame) is type(None):
            pass
        else:
            try:
                cv2.imshow('frame', frame)
                #stream.write(audio)
                if cv2.waitKey(25) == ord('q'):
                    client_socket.close()
                    exit(0)

            except:
                client_socket.close()
                exit(0)




finally:
    print("closing socket")
    client_socket.close()