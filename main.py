#####################################
#              Imports              #
#####################################

import socket  # for sending and receiving data
import os.path  # for checking if files exists
import re  # for getting the file extension
import renderers  # a custom python file with functions for rendering files

#####################################
#           Configuration           #
#####################################

# Soon, the configuration will be read from a file

config = {}

websiteDirectory = "./test_files/"  # where will the website run
defaultFile = "index.html"  # what file send by default to the site
port = 8080  # the webserver port
max_request_length = 1024  # max http request length
max_concurrent_connections = 10  # max concurrent connections
error_404_page = "404.html"  # path to the 404-error page
defaultHeaders = ""  # default get request headers
default_success_code = 200  # default success status code

#####################################
#            Functions              #
#####################################


def render_document(path_to_file):
    """
    :param path_to_file: the complete path to the file to be rendered
    :return: if the file can be rendered, it will be.

    This function dedicates to render the available formats. For example, if you pass it a php file, it will return
    the rendered version of it, instead of saying <php echo('hello') ?>, it will say hello.

    The functions written for rendering the formats are in the renderers.py script, more can be added by writing them
    into it and then adding it to the if-elif chain
    """
    extension = re.findall(r".+\.(\w+)", path_to_file)[0]  # get the extension using regex
    if extension == "php":
        return renderers.php(path_to_file)
    else:
        return renderers.default(path_to_file)


def read_file(file_path):
    """
    :param file_path: the complete path that the file will be read from
    :return: the file contents or the 404 page, the status of the file search 1 means 404 error

    This function dedicates to read a requested file from the webserver.
    If the file doesn't exist, these are the different cases:

    1) Return the 404-error page specified in the configuration.
    2) Create a custom 404-error page if the one specified doesn't exist.

    Then, if the file exists, it returns a status code of 0 and the file. If the file doesn't exist,
    it returns the 404 page and a status code of 1.
    """
    if os.path.isfile(config["websiteDirectory"] + file_path):  # check if the requested file exists
        status = 0
        file_data = render_document(config["websiteDirectory"] + file_path)  # read the requested file
    else:
        status = 1  # if the status is 1, it means the file wasn't found, a 404 error
        if os.path.isfile(config["websiteDirectory"] + config["error_404_page"]):  # check if the 404 page exists
            file_data = render_document(config["websiteDirectory"] + config["error_404_page"])
        else:
            file_data = "Please configure the 404-error page"  # custom 404-error page
    return file_data, status  # return them


def get_file_data(data):
    """
    :param data: the request that information will be got from
    :return: the http method, the file requested, the http version
    This function dedicates to process and extract basic information from a http request.
    Let's imagine this is the request we received:
        GET /index.html HTTP/1.1\n
        TAG: VALUE
        ...
    For later creating the response for it, we need three things:
        1) The operation (in this case: GET)
        2) The requested file (in this case: index.html)
        3) The http version, for answering with the same one (in this case: HTTP/1.1)
    The first thing we do, is grab only the first line, that's the place where the necessary info is.
    Then, we split that line by spaces, the first one is the operation, second one the file, third one the version.

    Finally, after we get the file, we check if its /, it means the client wants the default document, which we get from
    the settings.
    """
    first_line = data.split("\n")[0]  # get the first line
    # get the method, file, and version
    method_f = first_line.split(" ")[0]
    file_f = first_line.split(" ")[1]
    version_f = first_line.split(" ")[2]
    if file_f == "/":
        file_f = config["default_file"]  # use the default document when asked for it
    else:
        file_f = file_f[1:]  # crop the starting /, its more comfortable to work with it like that
    return method_f, file_f, version_f


# we will use this function to craft a response for a get request
def get_response_crafter(file_path, http_version, headers=config["defaultHeaders"],
                         status_code=config["default_success_code"]):
    """
    :param status_code: the successful status code to be returned
    :param file_path: the file to be read
    :param http_version: the http version that the client is using
    :param headers: the headers that will be added, defaults to an empty string
    :return: a complete response ready to be sent back to the client

    This function dedicates to create a response with code 200 for a get request, it gets the file using read_file()
    and if the file doesn't exist (the function returns a status of 1) it creates the same response but with a 404 code
    """
    file_data, status = read_file(file_path)  # get the file and status
    if status == 0:  # status 0 means a 200 status code
        content_f = http_version.strip("\r") + " " + status_code + "\n" + headers + "\n" + file_data
    else:  # other status means a 404 status code
        content_f = http_version.strip("\r") + " " + "404" + "\n" + headers + "\n" + file_data
    return content_f  # return it


######################################
#           Server Socket            #
######################################

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a normal tcp socket
# for a reason, the socket crashes saying that the address is already in use, even though it's not true. This solves it
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind(("0.0.0.0", int(config["port"])))  # we bind it to our real ip to make it visible to the real world
serverSocket.listen(config["max_concurrent_connections"])  # we start listening and accept 10 concurrent connections

while True:
    clientSocket, clientAddress = serverSocket.accept()  # accept client's connections
    request = clientSocket.recv(int(config["max_request_length"]))  # receive the client request
    method, fileName, version = get_file_data(request.decode())  # get the request details
    content = get_response_crafter(fileName, version)  # craft the response
    # send it and close the connection
    print(content)
    clientSocket.send(content.encode())
    clientSocket.close()
