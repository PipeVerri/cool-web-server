import os


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

    data = {}
    configFile = open("server_configuration", "r")

    for x in configFile.read().splitlines():
        line_without_comments = remove_comments(x)
        if line_without_comments is None:
            continue
        else:
            key_and_item = line_without_comments.split(" ", maxsplit=1)
            if key_and_item[0] == "default_headers":
                key_and_item[1] = key_and_item[1].replace(";", "\n")
            data[key_and_item[0]] = key_and_item[1]


class request_parsers:

    @staticmethod
    def parse_basic_request_information(data):
        first_line = data.split("\n")[0]
        http_method = first_line.split(" ")[0]
        http_file = first_line.split(" ")[1]
        http_version = first_line.split(" ")[2]
        if http_file == "/":
            http_file = configuration.data["default_file"]
        else:
            http_file = http_file[1:]
        return http_method, http_file, http_version


class file_parsers:
    @staticmethod
    def return_file_contents(file_path):
        if os.path.isfile(configuration.data["website_directory"] + file_path):
            file_exists = True
            file_contents = file_renderers.choose_renderer(configuration.data["website_directory"] + file_path)
        else:
            file_exists = False
            if os.path.isfile(configuration.data["website_directory"] + configuration.data["error_404_page"]):
                file_contents = file_renderers.choose_renderer(
                                configuration.data["website_directory"] + configuration.data["error_404_page"])
            else:
                file_contents = "Please configure the 404 page"
        return file_contents, file_exists


class response_crafters:
    @staticmethod
    def get_response_crafter(http_version, http_file, headers=configuration.data["default_headers"],
                             success_status_code=configuration.data["success_status_code"]):
        file_contents, file_exists = file_parsers.return_file_contents(http_file)
        if file_exists:
            return http_version + " " + success_status_code + "\n" + headers + "\n" + file_contents
        else:
            return http_version + " " + "404" + "\n" + headers + "\n" + file_contents


class file_renderers:
    @staticmethod
    def default(path_to_file):
        return open(path_to_file, "r").read()[1]

    @staticmethod
    def execute_file(command, path_to_file, args=""):
        args_encapsulated = '"' + args + '"'
        args_encapsulated.replace("\r", " ")
        return os.popen(f"{command} {path_to_file} {args_encapsulated}").read()

    @staticmethod
    def choose_renderer(file_to_render):
        return file_renderers.default(file_to_render)
