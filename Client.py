import cv2
import numpy as np
import time
import pyaudio
import socket
import wave
import pickle
import json
import threading

client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
vidBuffer = []
audioBuffer = []

def getVidData():
    print("connecting to localhost:8080")
    client_socket1.connect(('localhost', 8080))
    vid_data = client_socket1.recv(1024)
    print(vid_data.decode())
    try:
        while vid_data:
            # Stuff to get video frame size
            client_socket1.send("ready".encode())
            vid_data = client_socket1.recv(64)
            vid_data = vid_data.rstrip(b'\x00')
            data_str = vid_data.decode()
            frame_size = ord(data_str)

            print("Frame Size: " + str(frame_size))
            client_socket1.send("Got it".encode())

            #Get Frame
            vid_data = client_socket1.recv(frame_size)

            vidBuffer.append(vid_data)
            #print("Buffer Length: " + str(len(vidBuffer)))

        #print("whole video loaded")
    finally:
        print("closing socket 8080")
        client_socket1.close()

def getAudData():
    print("connecting to localhost:8081")
    client_socket2.connect(('localhost', 8081))
    aud_data = client_socket2.recv(1024)
    print(aud_data.decode())
    try:
        while aud_data:
            #Request Audio
            client_socket2.send("need audio".encode())

            #Stuff to get audio size
            aud_data = client_socket2.recv(1024)
            audio_size = int(aud_data.decode())
            print("Audio Size: " + str(audio_size))
            client_socket2.send("Got it".encode())

            #Get Audio
            audioBuffer.append(client_socket2.recv(7369))
            client_socket2.send("done".encode())
    finally:
        print("closing socket 8081")
        client_socket2.close()

def main():

    wf = wave.open("Man's Not Hot.wav")
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    threading.Thread(target=getVidData, args=[]).start()
    threading.Thread(target=getAudData, args=[]).start()
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
                    client_socket1.close()
                    client_socket2.close()
                    exit(0)
            except:
                client_socket1.close()
                client_socket2.close()
                exit(0)
        index += 1

main()