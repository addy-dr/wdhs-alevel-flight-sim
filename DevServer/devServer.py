import socket
import json

def main():
    host = '0.0.0.0'

    #can be any number not in use. Make sure to update datafile.txt though
    port = 12306

    server_socket = socket.socket(socket.AF_INET,
    socket.SOCK_STREAM) #use ipv4 and tcp
    
    server_socket.bind((host, port))
    server_socket.listen(5)  # Allow up to 5 queued connections

    print(f"Server listening on {host}:{port}")

    while True:
        connection, address = server_socket.accept()
        print(f"Connection from {address}")

        while True: #recieve the data
            data = connection.recv(1024).decode()
            if not data:
                break
            print("Data recieved")

            if data == 'rts': #request to send
                print("response sent")
                connection.sendall(b'cts') #clear to send
            else:
                datadict = json.loads(data)
                with open(f"error_logs/{datadict['timestamp']}.json", 'w') as file:
                    json.dump(datadict, file)
                connection.sendall(b"accepted")
                print("success")

        connection.close()

if __name__ == "__main__":
    main()
