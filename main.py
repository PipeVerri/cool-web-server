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
serverSocket.bind(("0.0.0.0", int(tools.configuration.data["port"])))
serverSocket.listen(tools.configuration.data["max_concurrent_connections"])

while True:
    clientSocket, clientAddress = serverSocket.accept()
    request = clientSocket.recv(int(tools.configuration.data["max_request_length"]))
    method, filename, version = tools.request_parsers.parse_basic_request_information(request.decode())

    if method == "POST":
        content = post_response_crafter(filename, version, request)
    elif method == "HEAD":
        content = head_response_crafter(filename, version)
    else:
        content = tools.response_crafters.get_response_crafter(filename, version)

    clientSocket.send(content.encode())
    clientSocket.close()
