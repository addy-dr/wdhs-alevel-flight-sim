import socket
import json
import os

def send_file(connection, filepath):
    with open(filepath, 'rb') as file:
        data = file.read()
        connection.sendall(data)

def sendFile(filepath):
    host = '127.0.0.1'
    port = 12303

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect((host, port))

    #first, send a rts message
    connection.sendall(b"rts")
    response = connection.recv(1024).decode()
    if response != "cts":
        print("an error has occured in the network connection.")
    else:
        # Send the JSON file
        send_file(connection, filepath)
        response = connection.recv(1024).decode()
        if response == "accepted":
            os.rename(filepath, "[sent]"+filepath)


    connection.close()

if __name__ == "__main__":
    sendFile("test.json")
