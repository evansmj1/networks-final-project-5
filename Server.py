import sys
import socket
import cv2
import time

cap = cv2.VideoCapture("Man's Not Hot.mp4")

serv_address = ('localhost', 8080)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind(serv_address)

sock.listen(1)

while True:
    print("Waiting to connect")

    new_connection, client_address = sock.accept()

    try:
        print('connection from', client_address)

        while (True):
            ret, frame = cap.read()

            data = cv2.imencode('.jpg', frame)[1].tostring()

            new_connection.send(data)
            #cv2.imshow('frame', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Closing connection with client. \n")
        new_connection.close()


