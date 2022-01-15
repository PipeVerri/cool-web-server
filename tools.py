import os
import re
import urllib.parse
from datetime import datetime
from collections import defaultdict
import magic


class InvalidRequest(Exception):
    pass


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
    methods = defaultdict(lambda: {"GET": True, "OPTIONS": True, "HEAD": True})
    configFile = open("server_configuration", "r")

    for x in configFile.read().splitlines():
        line_without_comments = remove_comments(x)
        if line_without_comments is None:
            continue
        else:
            key_and_value = line_without_comments.split(":", maxsplit=1)
            if line_without_comments[0] == ";":
                executors[key_and_value[0].strip(";")] = key_and_value[1]
            elif line_without_comments[0] == "*":
                methods_search = re.findall(r"([-+])(\w+)", key_and_value[1])
                dict_to_append = {}
                for y in methods_search:
                    method = y[1]
                    condition = False if y[0] == "-" else True
                    dict_to_append[method] = condition
                methods[key_and_value[0].strip("*")] = dict_to_append
            else:
                server[key_and_value[0]] = key_and_value[1]


class request_parsers:

    @staticmethod
    def validate_request(request):
        try:
            method, file, version = request_parsers.parse_basic_request_information(request)
        except InvalidRequest:
            return False, response_crafters.base_response_crafter(
                "HTTP/1.1", file_parsers.parse_file_path("404.html")[0], "400", 0) + "\r\n"
        if not (version in configuration.server["supported_versions"].split(",")):
            return False, response_crafters.base_response_crafter(
                version, file_parsers.parse_file_path("404.html")[0], "505", 0) + "\r\n"
        elif version == "HTTP/1.1" and len(re.findall(r"Host:\s.+", request)) == 0:
            return False, response_crafters.base_response_crafter(
                "HTTP/1.1", file_parsers.parse_file_path("404.html")[0], "400", 0) + "\r\n"
        elif len(re.findall(r".+\.\w+$", file)) == 0 and file[-1] != "/":
            return False, response_crafters.base_response_crafter(
                "HTTP/1.1", file_parsers.parse_file_path("404.html")[0], "200", 0, "application/octet-stream") + "\r\n"
        else:
            return True, None

    @staticmethod
    def parse_basic_request_information(data):
        try:
            first_line = data.split("\n")[0]
            http_method = first_line.split(" ")[0]
            http_file = urllib.parse.unquote(first_line.split(" ")[1])
            http_version = first_line.split(" ")[2]
            if http_file == "/":
                http_file = configuration.server["default_file"]
            else:
                http_file = re.findall(r"(http://\d+\.\d+\.\d+\.\d+:\d+)?/(.+)", http_file)[0][1]
            return http_method, http_file, http_version
        except IndexError:
            raise InvalidRequest


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
    def base_response_crafter(http_version, http_file, status_code, content_length, content_type=None):
        response = http_version + " " + status_code + " " + "OK" + "\r\n"
        response += "Connection: close" + "\r\n"
        response += "Date:" + datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT") + "\r\n"
        response += "Server: " + configuration.server["server_name"] + "\r\n"
        response += "Content-Length: " + str(content_length) + "\r\n"
        file_type = content_type if content_type is not None else magic.from_file(http_file, mime=True)
        response += "Content-Type: " + file_type + "\r\n"
        return response

    @staticmethod
    def get_response_crafter(http_version, http_file, headers=configuration.server["default_headers"]):
        path_updated, file_exists = file_parsers.parse_file_path(http_file)
        rendered_file = file_renderers.choose_renderer(path_updated)
        status_code = "200" if file_exists else "404"
        if rendered_file != b"":
            base_response = response_crafters.base_response_crafter(http_version, path_updated, status_code,
                                                                    os.path.getsize(path_updated))
        else:
            base_response = response_crafters.base_response_crafter(http_version, path_updated, status_code, 0,
                                                                    "text/plain")
            rendered_file = b""
        base_response += headers + "\r\n"
        base_response = base_response.encode() + rendered_file
        return base_response

    @staticmethod
    def head_response_crafter(http_version, http_file, headers=configuration.server["default_headers"]):
        path_updated, file_exists = file_parsers.parse_file_path(http_file)
        rendered_file = file_renderers.choose_renderer(path_updated)
        status_code = "200" if file_exists else "404"
        base_response = response_crafters.base_response_crafter(http_version, path_updated, status_code,
                                                                os.path.getsize(path_updated))
        base_response += headers + "\r\n"
        return base_response.encode()

    @staticmethod
    def options_response_crafter(http_version, http_file, headers=configuration.server["default_headers"]):
        path_updated, file_exists = file_parsers.parse_file_path(http_file)
        rendered_file = file_renderers.choose_renderer(path_updated)
        status_code = "200" if file_exists else "404"
        base_response = response_crafters.base_response_crafter(http_version, path_updated, status_code,
                                                                os.path.getsize(path_updated))
        allowed_methods = []
        for x in configuration.methods[http_file].items():
            if x[1]:
                allowed_methods.append(x[0])
        base_response += "Allow: " + ", ".join(allowed_methods) + "\r\n" + headers + "\r\n"
        return base_response.encode()

    @staticmethod
    def post_response_crafter(http_version, http_file, headers=configuration.server["default_headers"], args="test"):
        path_updated, file_exists = file_parsers.parse_file_path(http_file)
        rendered_file = file_renderers.choose_renderer(path_updated, args)
        status_code = "200" if file_exists else "501"
        base_response = response_crafters.base_response_crafter(http_version, path_updated, status_code,
                                                                os.path.getsize(path_updated))
        base_response += headers + "\r\n"
        base_response = base_response.encode() + rendered_file + b"\r\n"
        return base_response

    @staticmethod
    def trace_response_crafter(http_version, http_file, request, headers=configuration.server["default_headers"]):
        path_updated, file_exists = file_parsers.parse_file_path(http_file)
        rendered_file = file_renderers.choose_renderer(path_updated)
        status_code = "200"
        base_response = response_crafters.base_response_crafter(http_version, path_updated, status_code,
                                                                os.path.getsize(path_updated), "message/http")
        base_response += headers + "\r\n" + request
        return base_response.encode()


class file_renderers:
    @staticmethod
    def default(path_to_file):
        return open(path_to_file, "rb").read()

    @staticmethod
    def execute_file(command, path_to_file, args):
        args_encapsulated = '"' + args + '"'
        args_encapsulated.replace("\r", " ")
        return os.popen(f"{command} {path_to_file} {args_encapsulated}").read()

    @staticmethod
    def choose_renderer(file_to_render, args=""):
        extension = re.findall(r".+\.(\w+)", file_to_render)[0]
        if extension in configuration.executors.keys():
            return b"\r\n" + \
                   file_renderers.execute_file(configuration.executors[extension], file_to_render, args).encode()
        else:
            return file_renderers.default(file_to_render)


class loggers:

    @staticmethod
    def add_log(data):
        logs_file = open(configuration.server["log_file_path"], "a")
        line_to_append = ""
        for key, value in data.items():
            line_to_append += '"' + key + '"' + ":" + '"' + value + '"' + ";"
        line_to_append += "\n"
        logs_file.write(line_to_append)
        logs_file.close()

    @staticmethod
    def log_request(request, client_socket="", client_address=""):
        method, file, version = request_parsers.parse_basic_request_information(request)
        log_data = {"method": method, "file": file, "version": version}
        for x in request.split("\n")[1:]:
            if x == " " or x == "":
                continue
            header, value = x.split(" ", maxsplit=1)
            log_data[header.strip(":")] = value[:-1]
        loggers.add_log(log_data)
