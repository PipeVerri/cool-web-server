import socket
import os

path = "./run_directory"

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(("0.0.0.0", 8080))
serverSocket.listen(10)

while True:
    clientSocket, clientAddress = serverSocket.accept()
    data = clientSocket.recv(1024)
    print(data)