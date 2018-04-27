import cv2
import numpy as np
import time
import pyaudio
import socket
import wave
import pickle
import json
import threading

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
vidBuffer = []


def getData():
    print("connecting to localhost")
    client_socket.connect(('localhost', 8080))
    data = client_socket.recv(1024)
    try:
        while data:
            data = client_socket.recv(500000)
            vidBuffer.append(data)

        print("whole video loaded")

    finally:
        print("closing socket")
        client_socket.close()

def main():

    wf = wave.open("Man's Not Hot.wav")
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    threading.Thread(target=getData, args=[]).start()
    while len(vidBuffer) < 20:
        print(len(vidBuffer))

    index = 0
    while True:
        if index == len(vidBuffer):
            time.sleep(2)
        nparr = np.fromstring(vidBuffer[index], np.uint8)

        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if type(frame) is type(None):
            pass
        else:
            try:
                cv2.imshow('frame', frame)
                if cv2.waitKey(41) == ord('q'):
                    client_socket.close()
                    exit(0)
            except:
                client_socket.close()
                exit(0)
        index += 1
    #data = client_socket.recv(1024)

    # try:
            #while data:
            #print("receiving data")
            #data = client_socket.recv(500000)

            #print(data.decode('utf-8'))
            #data = json.loads(data.decode('utf-8'))
            #audio = client_socket.recv(500000)


            #nparr = np.fromstring(data, np.uint8)


            #frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)


    #         if type(frame) is type(None):
    #             pass
    #         else:
    #             try:
    #                 cv2.imshow('frame', frame)
    #                 #stream.write(audio)
    #                 if cv2.waitKey(25) == ord('q'):
    #                     client_socket.close()
    #                     exit(0)
    #
    #             except:
    #                 client_socket.close()
    #                 exit(0)
    #
    #
    #
    #
    # finally:
    #     print("closing socket")
    #     client_socket.close()



main()