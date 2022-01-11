#####################################
#              Imports              #
#####################################

import socket  # for sending and receiving data
import tools

######################################
#           Server Socket            #
######################################

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind(("0.0.0.0", int()))
serverSocket.listen(tools.configuration.data["max_concurrent_connections"])

while True:
    clientSocket, clientAddress = serverSocket.accept()
    request = clientSocket.recv(int(tools.configuration.data["max_request_length"]))
    method, fileName, version = get_file_data(request.decode())

    if method == "POST":
        content = post_response_crafter(fileName, version, request)
    elif method == "HEAD":
        content = head_response_crafter(fileName, version)
    else:
        content = get_response_crafter(fileName, version)

    clientSocket.send(content.encode())
    clientSocket.close()
