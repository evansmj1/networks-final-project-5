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
audioBuffer = []

def getData():
    print("connecting to localhost")
    client_socket.connect(('localhost', 8080))
    vid_data = client_socket.recv(1024)
    print(vid_data.decode())
    try:
        while vid_data:
            # current_step = client_socket.recv(1024)

            # Stuff to get video frame size
            client_socket.send("ready".encode())
            vid_data = client_socket.recv(1024)
            frame_size = int(vid_data.decode())

            print("Frame Size: " + str(frame_size))
            client_socket.send("Got it".encode())

            #Get Frame
            vid_data = client_socket.recv(500000)

            vidBuffer.append(vid_data)
            #print("Buffer Length: " + str(len(vidBuffer)))

            #Request Audio
            client_socket.send("need audio".encode())

            #Stuff to get audio size
            audio_data = client_socket.recv(1024)
            audio_size = int(audio_data.decode())
            print("Audio Size: " + str(audio_size))
            client_socket.send("Got it".encode())

            #Get Audio
            audioBuffer.append(client_socket.recv(7369))
            client_socket.send("done".encode())

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
        #print(len(vidBuffer))
        pass

    index = 1
    print("Buffer: " + str(len(vidBuffer)))
    while True:
        if index == (len(vidBuffer) - 1):
            print("Index: " + str(index))
            time.sleep(2)
        nparr = np.fromstring(vidBuffer[index], np.uint8)

        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if type(frame) is type(None):
            print("BAD DATA")
            pass
        else:
            try:
                cv2.imshow('frame', frame)
                stream.write(audioBuffer[index])
                print("Current index: " + str(index))
                #print("Buffer length: " + str(len(vidBuffer)))
                if cv2.waitKey(41) == ord('q'):
                    client_socket.close()
                    exit(0)
            except:
                client_socket.close()
                exit(0)
        index += 1

main()