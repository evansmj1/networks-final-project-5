import sys
import socket
import cv2
import time
import pyaudio
import wave
import numpy
import pickle
import json
import threading


def main():
    CHUNK = 1838

    cap = cv2.VideoCapture("Man's Not Hot.mp4")

    serv_address1 = ('localhost', 8080)
    serv_address2 = ('localhost', 8081)

    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock1.bind(serv_address1)
    sock2.bind(serv_address2)

    wf = wave.open("Man's Not Hot.wav")

    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    frames_per_buffer=CHUNK)
    print("Sample Width: " + str(wf.getsampwidth()))
    print("Channels: " + str(wf.getnchannels()))
    print("Frame Rate: " + str(wf.getframerate()))

    sock1.listen(1)
    sock2.listen(1)

    while True:
        print("Waiting to connect")

        new_connection1, client_address1 = sock1.accept()
        new_connection2, client_address2 = sock2.accept()

        try:
            #print('connection from', client_address)

            new_connection1.send("Starting".encode())
            while True:
                ret, frame = cap.read()
                audio = wf.readframes(CHUNK)

                frame_data = cv2.imencode('.jpg', frame)[1]

                new_connection1.recv(1024)
                #strsize = 64 - sys.getsizeof(str(sys.getsizeof(frame_data)).encode())
                strsize = 64 - sys.getsizeof(chr(sys.getsizeof(frame_data)).encode())
                pad_data = chr(sys.getsizeof(frame_data)).encode() + ("\0"*strsize).encode()
                print(pad_data)
                print(sys.getsizeof(pad_data))
                new_connection1.send(pad_data)
                new_connection1.recv(1024)
                new_connection1.send(frame_data)

               # print("sending frame")

                print('Receiving audio handshake...')
                # getting stuck on this recv
                new_connection2.recv(1024)
                print('received handshake')
                new_connection2.send(str(sys.getsizeof(audio)).encode())
                print("Audio Size: " + str(sys.getsizeof(audio)))
                new_connection2.recv(1024)
                new_connection2.send(audio)
                new_connection2.recv(1024)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("Closing connection with client. \n")
            new_connection1.close()
            new_connection2.close()

main()
