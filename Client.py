import cv2
import numpy as np
import time
import pyaudio
import socket
import wave
import pickle
import json
import threading
import multiprocessing

client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
vidBuffer = []
audioBuffer = []
playbackIndex = 0

def getVidData():
    print("connecting to localhost:8080")
    client_socket1.connect(('localhost', 8080))
    vid_data = client_socket1.recv(1024)
    print(vid_data.decode())
    client_socket1.send("Ready".encode())
    try:
        while vid_data:
            vid_data = client_socket1.recv(500000)
            client_socket1.send("Got it".encode())
            vidBuffer.append(vid_data)

        print("whole video loaded")
    finally:
        print("closing socket 8080")
        client_socket1.close()

def getAudData():
    print("connecting to localhost:8081")
    client_socket2.connect(('localhost', 8081))
    aud_data = client_socket2.recv(1024)
    print(aud_data.decode())
    client_socket2.send("ready".encode())
    try:
        while aud_data:
            audioBuffer.append(client_socket2.recv(7369))
    finally:
        print("closing socket 8081")
        client_socket2.close()

def playVideo():
    global playbackIndex
    #wf = wave.open("Man's Not Hot.wav")
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(2),
                    channels=2,
                    rate=44100,
                    output=True)
    print("Audio initial index: " + str(playbackIndex))
    #while audioBuffer[playbackIndex] is not None:

    print("In video thread")
    while vidBuffer[playbackIndex] is not None:
        #audioProc = multiprocessing.Process(target=stream.write(audioBuffer[playbackIndex]), args=[])
        nparr = np.fromstring(vidBuffer[playbackIndex], np.uint8)

        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if type(frame) is type(None):
            print("BAD DATA")
            pass
        else:
            try:
                #cv2.imshow('frame', frame)
                cv2.imshow('frame', frame)
                #stream.write(audioBuffer[playbackIndex])
                #audioProc.start()
                #print("Current index: " + str(playbackIndex))
                # print("Buffer length: " + str(len(vidBuffer)))
                key = cv2.waitKey(41)
                if key == ord('q'):
                    client_socket1.close()
                    client_socket2.close()
                    exit(0)

                if key == ord('a') and playbackIndex > 5:
                    playbackIndex -= 5
                if key == ord('d') and playbackIndex < len(vidBuffer) - 6 and playbackIndex < len(audioBuffer) - 6:
                    playbackIndex += 5
                if key == ord('p'):
                    while True:
                        unpause = cv2.waitKey(1)
                        if (unpause == ord('p')):
                            break

            except:
                client_socket1.close()
                client_socket2.close()
                exit(0)
        playbackIndex += 1


def playAudio():
    global playbackIndex


def main():

    threading.Thread(target=getVidData, args=[]).start()
    threading.Thread(target=getAudData, args=[]).start()
    while len(vidBuffer) < 20:
        print(len(vidBuffer))
        pass

    index = 1
    print("Buffer: " + str(len(vidBuffer)))

    threading.Thread(target=playVideo(),args=[]).start()

main()