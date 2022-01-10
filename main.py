#####################################
#              Imports              #
#####################################

import socket  # for sending and receiving data
import os.path  # for checking if files exists
import re  # for getting the file extension
import parsers  # a custom python file with functions for rendering files

#####################################
#           Configuration           #
#####################################

config = {}
config_file = open("server_configuration", "r")


def remove_comments(line):
    if (line == "") or (line[0] == "#"):
        return None
    elif "#" in line:
        index_to_strip_to = line.find("#") - 1
        return line[:index_to_strip_to]
    else:
        return line


for x in config_file.read().splitlines():
    config_line = remove_comments(x)
    if config_line is None:
        continue
    else:
        key_and_value = config_line.split(" ", maxsplit=1)
        config[key_and_value[0].strip(":")] = key_and_value[1].replace(";", "\n")


#####################################
#            Functions              #
#####################################


def render_document(path_to_file):
    extension = re.findall(r".+\.(\w+)", path_to_file)[0]
    if extension in parsers.extensionCommand.keys():
        return parsers.execute_file(parsers.extensionCommand[extension], path_to_file)
    else:
        return parsers.default(path_to_file)


def parse_file_path(file_path):
    if os.path.isfile(config["websiteDirectory"] + file_path):
        status = 0
        file_data = config["websiteDirectory"] + file_path
    else:
        if os.path.isfile(config["websiteDirectory"] + config["error_404_page"]):
            status = 1
            file_data = config["websiteDirectory"] + config["error_404_page"]
        else:
            status = 2
            file_data = "Please configure the 404-error page"
    return file_data, status


def get_file_data(data):
    first_line = data.split("\n")[0]
    method_f = first_line.split(" ")[0]
    file_f = first_line.split(" ")[1]
    version_f = first_line.split(" ")[2]
    if file_f == "/":
        file_f = config["default_file"]
    else:
        file_f = file_f[1:]
    return method_f, file_f, version_f


def get_response_crafter(file_path, http_version, headers=config["defaultHeaders"],
                         status_code=config["default_success_code"]):
    path_parsed, status = parse_file_path(file_path)
    if status == 0:
        content_f = http_version.strip("\r") + " " + status_code + "\n" + headers + "\n" + render_document(path_parsed)
    elif status == 2:
        content_f = http_version.strip("\r") + " " + "404" + "\n" + headers + "\n" + render_document(path_parsed)
    else:
        content_f = http_version.strip("\r") + " " + "404" + "\n" + headers + "\n" + path_parsed
    return content_f


def post_response_crafter(file_path, http_version, request_data):
    path_parsed, status = parse_file_path(file_path)
    extension = re.findall(r".+\.(\w+)", path_parsed)[0]
    if extension in parsers.extensionCommand.keys():
        return parsers.execute_file(parsers.extensionCommand[extension], path_parsed, request_data)
    else:
        return get_response_crafter(file_path, http_version)


######################################
#           Server Socket            #
######################################

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a normal tcp socket
# for a reason, the socket crashes saying that the address is already in use, even though it's not true. This solves it
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind(("0.0.0.0", int(config["port"])))  # we bind it to our real ip to make it visible to the real world
serverSocket.listen(int(config["max_concurrent_connections"]))  # we start listening with max 10 concurrent connections

while True:
    clientSocket, clientAddress = serverSocket.accept()  # accept client's connections
    request = clientSocket.recv(int(config["max_request_length"]))  # receive the client request
    method, fileName, version = get_file_data(request.decode())  # get the request details
    content = get_response_crafter(fileName, version)  # craft the response
    # send it and close the connection
    print(content)
    clientSocket.send(content.encode())
    clientSocket.close()
