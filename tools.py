import os
import re
from datetime import datetime
import sys
import magic


class configuration:

    @staticmethod
    def remove_comments(line):
        if (line == "") or (line[0] == "#"):
            return None
        elif "#" in line:
            index_to_strip_to = line.find("#") - 1
            return line[:index_to_strip_to]
        else:
            return line

    server = {}
    executors = {}
    configFile = open("server_configuration", "r")

    for x in configFile.read().splitlines():
        line_without_comments = remove_comments(x)
        if line_without_comments is None:
            continue
        else:
            line_without_comments = line_without_comments.replace(";", "\r\n")
            key_and_value = line_without_comments.split(":", maxsplit=1)
            if line_without_comments[0] == ";":
                executors[key_and_value[0].strip(";")] = key_and_value[1]
            else:
                server[key_and_value[0]] = key_and_value[1]


class request_parsers:

    @staticmethod
    def parse_basic_request_information(data):
        try:
            first_line = data.split("\n")[0]
            http_method = first_line.split(" ")[0]
            http_file = first_line.split(" ")[1]
            http_version = first_line.split(" ")[2]
            if http_file == "/":
                http_file = configuration.server["default_file"]
            else:
                http_file = re.findall(r"(http://\d+\.\d+\.\d+\.\d+:\d+)?/(.+)", http_file)[0][1]
                print(http_file)
            return http_method, http_file, http_version
        except IndexError:
            http_method = "GET"
            http_file = "/"
            http_version = "HTTP/1.1"
            return http_method, http_file, http_version


class file_parsers:
    @staticmethod
    def parse_file_path(file_path):
        if os.path.isfile(configuration.server["website_directory"] + file_path):
            file_exists = True
            updated_path = configuration.server["website_directory"] + file_path
        else:
            file_exists = False
            if os.path.isfile(configuration.server["website_directory"] + configuration.server["error_404_page"]):
                updated_path = configuration.server["website_directory"] + configuration.server["error_404_page"]
            else:
                raise Exception("Please configure the 404 page")
        return updated_path, file_exists


class response_crafters:
    @staticmethod
    def base_response_crafter(http_version, http_file, status_code, content_length):
        response = http_version + " " + status_code + " " + "OK" + "\r\n"
        response += "Connection: close" + "\r\n"
        response += "Date:" + datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT") + "\r\n"
        response += "Server: " + configuration.server["server_name"] + "\r\n"
        response += "Content-Length: " + str(content_length) + "\r\n"
        response += "Content-Type: " + magic.from_file(http_file, mime=True) + "\r\n"
        return response

    @staticmethod
    def get_response_crafter(http_version, http_file, headers=configuration.server["default_headers"]):
        path_updated, file_exists = file_parsers.parse_file_path(http_file)
        rendered_file = file_renderers.choose_renderer(path_updated)
        status_code = "200" if file_exists else "404"
        base_response = response_crafters.base_response_crafter(http_version, path_updated, status_code,
                                                                sys.getsizeof(rendered_file))
        base_response += headers + "\r\n" + rendered_file + "\r\n"
        return base_response

    @staticmethod
    def head_response_crafter(http_version, http_file, headers=configuration.server["default_headers"]):
        path_updated, file_exists = file_parsers.parse_file_path(http_file)
        rendered_file = file_renderers.choose_renderer(path_updated)
        status_code = "200" if file_exists else "404"
        base_response = response_crafters.base_response_crafter(http_version, path_updated, status_code,
                                                                sys.getsizeof(rendered_file))
        base_response += headers + "\r\n"
        return base_response

    @staticmethod
    def post_response_crafter(http_version, http_file, headers=configuration.server["default_headers"], args="test",
                              use_template=configuration.server["post_response_template"]):
        updated_path, file_exists = file_parsers.parse_file_path(http_file)
        rendered_file = file_renderers.choose_renderer(updated_path, args)
        if file_exists:
            if use_template == "true":
                return http_version + " " + configuration.server["success_status_code"] + headers + rendered_file
            else:
                return rendered_file
        else:
            return http_version + " " + configuration.server["file_not_found_status_code"] + "\r\n" + \
                   headers + "\r\n" + rendered_file


class file_renderers:
    @staticmethod
    def default(path_to_file):
        return open(path_to_file, "r").read()

    @staticmethod
    def execute_file(command, path_to_file, args):
        args_encapsulated = '"' + args + '"'
        args_encapsulated.replace("\r", " ")
        return os.popen(f"{command} {path_to_file} {args_encapsulated}").read()

    @staticmethod
    def choose_renderer(file_to_render, args=""):
        extension = re.findall(r".+\.(\w+)", file_to_render)[0]
        if extension in configuration.executors.keys():
            return "\r\n" + file_renderers.execute_file(configuration.executors[extension], file_to_render, args)
        else:
            return "\r\n" + file_renderers.default(file_to_render)
