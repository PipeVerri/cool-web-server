import os
import re
from datetime import datetime
import sys
from collections import defaultdict
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
        is_request_valid = False
        try:
            method, file, version = request_parsers.parse_basic_request_information(request)
        except IndexError:
            is_request_valid = False
            return is_request_valid, response_crafters.base_response_crafter(
                "HTTP/1.1", file_parsers.parse_file_path("404.html")[0], "400", 0) + "\r\n"
        if not (version in configuration.server["supported_versions"].split(",")):
            return is_request_valid, response_crafters.base_response_crafter(
                version, file_parsers.parse_file_path("404.html")[0], "505", 0) + "\r\n"
        else:
            return True, None

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
            return http_method, http_file, http_version
        except IndexError:
            raise IndexError


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
    def options_response_crafter(http_version, http_file, headers=configuration.server["default_headers"]):
        path_updated, file_exists = file_parsers.parse_file_path(http_file)
        rendered_file = file_renderers.choose_renderer(path_updated)
        status_code = "200" if file_exists else "404"
        base_response = response_crafters.base_response_crafter(http_version, path_updated, status_code,
                                                                sys.getsizeof(rendered_file))
        allowed_methods = []
        for x in configuration.methods[http_file].items():
            if x[1]:
                allowed_methods.append(x[0])
        base_response += "Allow: " + ", ".join(allowed_methods) + "\r\n" + headers + "\r\n"
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
