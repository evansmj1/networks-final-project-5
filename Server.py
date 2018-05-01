import socket
import cv2
import pyaudio
import wave


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
            print('connection from', client_address1)
            new_connection1.send("Starting".encode())
            new_connection1.recv(1024)

            new_connection2.send("Starting".encode())
            new_connection2.recv(1024)
            while True:
                ret, frame = cap.read()
                audio = wf.readframes(CHUNK)

                frame_data = cv2.imencode('.jpg', frame)[1]

                new_connection1.send(frame_data)

                new_connection2.send(audio)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("Closing connection with client. \n")
            new_connection1.close()
            new_connection2.close()

main()
