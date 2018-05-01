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
vidIndex = 0
audIndex = 0
audioNeedsToWait = False
videoNeedsToWait = False
rewind = False
forward = False
pause = False
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
    global vidIndex
    global videoNeedsToWait
    global rewind
    global forward
    global pause
    #wf = wave.open("Man's Not Hot.wav")

    print("In video thread")
    while vidIndex < len(vidBuffer) - 1:
        if (vidIndex == len(vidBuffer) - 5):
            videoNeedsToWait = True
            while (vidIndex > len(vidBuffer) - 20 or audioNeedsToWait):
                cv2.waitKey(1)
            videoNeedsToWait = False

        #audioProc = multiprocessing.Process(target=stream.write(audioBuffer[playbackIndex]), args=[])
        nparr = np.fromstring(vidBuffer[vidIndex], np.uint8)

        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if type(frame) is type(None):
            #print("BAD DATA")
            pass
        else:
            try:
                #cv2.imshow('frame', frame)
                #threading.Thread(target=stream.write, kwargs={'frames': audio}).start()
                cv2.imshow('frame', frame)
                #stream.write(audioBuffer[playbackIndex])
                #audioProc.start()
                #print("Current index: " + str(playbackIndex))
                # print("Buffer length: " + str(len(vidBuffer)))
                key = cv2.waitKey(21)
                if key == ord('q'):
                    client_socket1.close()
                    client_socket2.close()
                    exit(0)

                if key == ord('a') and vidIndex > 5:
                    rewind = True
                    vidIndex -= 5
                if key == ord('d') and vidIndex < len(vidBuffer) - 6:
                    forward = True
                    vidIndex += 5
                if key == ord('p'):
                    pause = True
                    while True:
                        unpause = cv2.waitKey(1)
                        if (unpause == ord('p')):
                            pause = False
                            break

            except:
                client_socket1.close()
                client_socket2.close()
                exit(0)
        vidIndex += 1


def playAudio():
    global audIndex
    global vidIndex
    global audioNeedsToWait
    global rewind
    global forward
    global pause

    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(2),
                    channels=2,
                    rate=44100,
                    output=True)

    while (audIndex < len(audioBuffer) - 1):

        stream.write(audioBuffer[audIndex])
        if rewind:
            audIndex -= 5
            rewind = False
        if forward:
            audIndex += 5
            forward = True
        if pause:
            while pause:
                pass

        if audIndex > vidIndex + 1:
            pass
        else:
            #audIndex = vidIndex
            audIndex += 1
def main():

    threading.Thread(target=getVidData, args=[]).start()
    threading.Thread(target=getAudData, args=[]).start()
    while len(vidBuffer) < 100:
        #print(len(vidBuffer))
        pass

    #print("Buffer: " + str(len(vidBuffer)))

    threading.Thread(name="video",target=playVideo,args=[]).start()
    threading.Thread(name="audio",target=playAudio, args=[]).start()



main()