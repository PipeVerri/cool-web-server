#####################################
#              Imports              #
#####################################

import socket  # for sending and receiving data
import re  # for parsing strings

#####################################
#           Configuration           #
#####################################

websiteDirectory = "./run_directory/"  # where will the website run
defaultFile = "index.html"  # what file send by default to the site
port = 8081
max_request_length = 1024
max_concurrent_connections = 10

#####################################
#            Functions              #
#####################################


# we will use this function in the future for rendering other formats, like php
def read_document(path):
    try:  # we try reading the data, if we can't, we return None
        data = open(websiteDirectory + path, "r").read()
    except FileNotFoundError:
        return None
    return data


# we will use this function for basic request data
def get_file_data(data):
    file_f = data.split("\n")[0].split(" ")[1]  # we get the first line, and then we get the second element
    if file_f == "/":  # if the file is only /, the client is asking for the default document
        file_f = defaultFile
    else:  # if the path is correct, we remove the starting /
        file_f = file_f[1:]
    # we get the version and method using the same method as before
    method_f = data.split("\n")[0].split(" ")[0]
    version_f = data.split("\n")[0].split(" ")[2]
    return method_f, file_f, version_f  # return it


# we will use this function to craft a response for a get request
def get_response_crafter(file_name, http_version, headers="", status_code="200"):
    content_f = http_version.strip("\r") + " " + status_code + "\n" + headers + "\n"  # create a base response
    file_data = read_document(file_name)  # get the html code
    if file_data is None:  # if the function couldn't find the file, return 404 response
        content_f = http_version.strip("\r") + " " + "404"
    else:
        content_f += file_data  # else, add it to the base response
    return content_f


######################################
#           Server Socket            #
######################################

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a normal tcp socket
serverSocket.bind(("0.0.0.0", port))  # we bind it to our real ip to make it visible to the real world
serverSocket.listen(max_concurrent_connections)  # we start listening and accept 10 concurrent connections

while True:
    clientSocket, clientAddress = serverSocket.accept()  # accept client's connections
    request = clientSocket.recv(max_request_length)  # receive the client request
    method, fileName, version = get_file_data(request.decode())  # get the request details
    content = get_response_crafter(fileName, version)  # craft the response
    # send it and close the connection
    print(content)
    clientSocket.send(content.encode())
    clientSocket.close()