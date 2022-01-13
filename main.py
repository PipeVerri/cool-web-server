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
    decoded_request = request.decode().replace("\r", " ")
    is_request_valid, error_response = tools.request_parsers.validate_request(decoded_request)
    content = ""
    if is_request_valid:
        method, filename, version = tools.request_parsers.parse_basic_request_information(decoded_request)
    else:
        method, version, filename = None, None, None
        content = error_response
    if method == "POST":
        content = tools.response_crafters.post_response_crafter(version, filename, args=decoded_request)
    elif method == "HEAD":
        content = tools.response_crafters.head_response_crafter(version, filename)
    elif method == "OPTIONS":
        content = tools.response_crafters.options_response_crafter(version, filename)
    elif method == "GET":
        content = tools.response_crafters.get_response_crafter(version, filename)
    print(content.encode())
    clientSocket.send(content.encode())
    clientSocket.close()
