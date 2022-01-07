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

#####################################
#            Functions              #
#####################################


def get_request_information(data):
    print(data)


######################################
#           Server Socket            #
######################################

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a normal tcp socket
serverSocket.bind((socket.gethostname(), 8080))  # we bind it to our real ip to make it visible to the real world
serverSocket.listen(10)  # we start listening and accept 10 concurrent connections

while True:
    clientSocket, clientAddress = serverSocket.accept()
    request = clientSocket.recv(1024)
    get_request_information(request.decode())
