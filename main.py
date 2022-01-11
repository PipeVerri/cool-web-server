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
serverSocket.bind(("0.0.0.0", int(tools.configuration.server["port"])))
serverSocket.listen(int(tools.configuration.server["max_concurrent_connections"]))

while True:
    clientSocket, clientAddress = serverSocket.accept()
    request = clientSocket.recv(int(tools.configuration.server["max_request_length"]))
    method, filename, version = tools.request_parsers.parse_basic_request_information(request.decode())
    version.strip("\r")
    if method == "POST":
        content = tools.response_crafters.post_response_crafter(version, filename, request.decode())
    else:
        content = tools.response_crafters.get_response_crafter(version, filename)
    clientSocket.send(content.encode())
    clientSocket.close()
