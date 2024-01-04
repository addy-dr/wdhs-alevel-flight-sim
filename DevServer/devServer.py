import socket

HOST = "127.0.0.1" #localhost
PORT = 65432  #port

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket: #use ipv4 and tcp
    socket.bind((HOST, PORT)) #bind to host and port
    socket.listen()
    conn, addr = socket.accept() #connection, address
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)