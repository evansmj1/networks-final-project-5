import cv2
import numpy as np
import pyaudio
import socket
import threading

#Sockets for easy access throughout
client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#The arrays we store the data into
vidBuffer = []
audioBuffer = []

#Indices for audio and video playback in loops
vidIndex = 0
audIndex = 0

#Variables to allow the commands to propogate to the audio instead of just the video
rewind = False
forward = False
pause = False

#So that we know the difference between catching up to buffering and actually finishing
videoFinished = False
audioFinished = False

#Gets the video from the Server
def getVidData():
    global videoFinished
    print("connecting to localhost:8080")
    client_socket1.connect(('localhost', 8080))

    #Makes sure we're ready
    vid_data = client_socket1.recv(1024)
    client_socket1.send("Ready".encode())
    try:
        #While there are frames left, put them into the buffer
        while vid_data:
            vid_data = client_socket1.recv(500000)
            client_socket1.send("Got it".encode())
            vidBuffer.append(vid_data)

    finally:
        videoFinished = True
        print("closing socket 8080")
        client_socket1.close()

#Gets the audio from the server
def getAudData():
    global audioFinished
    print("connecting to localhost:8081")
    client_socket2.connect(('localhost', 8081))
    aud_data = client_socket2.recv(1024)
    client_socket2.send("ready".encode())
    try:
        #While there is audio left, put it into the buffer
        while aud_data:
            audioBuffer.append(client_socket2.recv(7369))
    finally:
        audioFinished = True
        print("closing socket 8081")
        client_socket2.close()

#Plays the video
def playVideo():
    global vidIndex
    global rewind
    global forward
    global pause

    #While there is video remaining
    while vidIndex < len(vidBuffer) - 1:
        #If the playback isn't near the end of the buffer, give it time to load more
        if audIndex < len(audioBuffer) - 10 and vidIndex < len(vidBuffer) - 10 and not videoFinished:

            #Set up the frame
            nparr = np.fromstring(vidBuffer[vidIndex], np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            #If the frame got corrupted, don't play it
            if type(frame) is type(None):
                #print("BAD DATA")
                pass
            else:
                try:
                    #Show the frame
                    cv2.imshow('frame', frame)
                    #Wait according to the frame rate
                    key = cv2.waitKey(21)

                    #If "q" is pressed, quit
                    if key == ord('q'):
                        client_socket1.close()
                        client_socket2.close()
                        exit(0)

                    #If "a" is pressed, rewind
                    if key == ord('a') and vidIndex > 5:
                        rewind = True
                        vidIndex -= 5

                    #If "d" is pressed, fast forward
                    if key == ord('d') and vidIndex < len(vidBuffer) - 6:
                        forward = True
                        vidIndex += 5

                    #If "p" is pressed, pause
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
    global rewind
    global forward
    global pause

    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(2),
                    channels=2,
                    rate=44100,
                    output=True)

    while audIndex < len(audioBuffer) - 1:
        if audIndex < len(audioBuffer) - 10 and vidIndex < len(vidBuffer) - 10 and not audioFinished:
            stream.write(audioBuffer[audIndex])

            #If rewinding in video, rewind audio
            if rewind:
                audIndex -= 5
                rewind = False
            #If fast forwarding video, fast forward audio
            if forward:
                audIndex += 5
                forward = True
            #if pausing video, pause audio
            if pause:
                while pause:
                    pass

            #If the audio is ahead of the video, let the video catch up
            if audIndex > vidIndex + 1:
                pass
            else:
                audIndex += 1
def main():

    threading.Thread(target=getVidData, args=[]).start()
    threading.Thread(target=getAudData, args=[]).start()
    while len(vidBuffer) < 100:
        pass

    threading.Thread(name="video",target=playVideo,args=[]).start()
    threading.Thread(name="audio",target=playAudio, args=[]).start()



main()