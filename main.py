#####################################
#              Imports              #
#####################################

import socket  # for sending and receiving data
import re  # for parsing strings

#####################################
#           Configuration           #
#####################################

websiteDirectory = "./run_directory"  # where will the website run
defaultFile = "index.html"  # what file send by default to the site

#####################################
#            Functions              #
#####################################


# we will use this function in the future for rendering other formats, like php
def read_document(path):
    data = open(path, "r").read()
    return data


# we will use this function for getting the content for the client
def get_file_data(data):
    file_path = data.split("\n").split(" ")[1]  # we get the first line, and then we get the second element
    if file_path == "":  # if the file is /, the client is asking for the default document
        file_path = defaultFile
    file_data = read_document(websiteDirectory + file_path)
    return file_data


######################################
#           Server Socket            #
######################################

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a normal tcp socket
serverSocket.bind(("0.0.0.0", 8080))  # we bind it to our real ip to make it visible to the real world
serverSocket.listen(10)  # we start listening and accept 10 concurrent connections

while True:
    clientSocket, clientAddress = serverSocket.accept()
    request = clientSocket.recv(1024)
    content = get_file_data(request.decode())
