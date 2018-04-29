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

    serv_address = ('localhost', 8080)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind(serv_address)

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

    sock.listen(1)


    while True:
        print("Waiting to connect")

        new_connection, client_address = sock.accept()

        try:
            print('connection from', client_address)

            new_connection.send("Starting".encode())
            while True:
                ret, frame = cap.read()
                audio = wf.readframes(CHUNK)

                frame_data = cv2.imencode('.jpg', frame)[1]

                new_connection.recv(1024)
                print("String size: " + str(sys.getsizeof(str(sys.getsizeof(frame_data)).encode())))
                new_connection.send(str(sys.getsizeof(frame_data)).encode())
                new_connection.recv(1024)
                new_connection.send(frame_data)

               # print("sending frame")

                new_connection.recv(1024)
                new_connection.send(str(sys.getsizeof(audio)).encode())
                print("Audio Size: " + str(sys.getsizeof(audio)))
                new_connection.recv(1024)
                new_connection.send(audio)
                new_connection.recv(1024)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("Closing connection with client. \n")
            new_connection.close()


main()
