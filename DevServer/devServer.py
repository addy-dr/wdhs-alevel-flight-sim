import socket
import json

def main():
    host = '127.0.0.1'
    port = 12303 #can be any number not in use

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #use ipv4 and tcp
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
                try:
                    datadict = json.loads(data)
                    with open(f"{datadict['timestamp']}.json", 'w') as file:
                        json.dump(datadict, file)
                    connection.sendall(b"accepted")
                except:
                    pass #the data is not in json format and thus should be ignored

        connection.close()

if __name__ == "__main__":
    main()
