#####################################
#              Imports              #
#####################################

import socket
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
    print(request)
    decoded_request = request.decode().replace("\r", " ")
    method, filename, version = tools.request_parsers.parse_basic_request_information(decoded_request)
    if method == "POST":
        content = tools.response_crafters.post_response_crafter(version, filename, args=decoded_request)
    else:
        content = tools.response_crafters.get_response_crafter(version, filename)
    print(content.encode())
    clientSocket.send(content.encode())
    clientSocket.close()
