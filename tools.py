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
            data[key_and_item[0]] = key_and_item[1]


class file_parsers:

    @staticmethod
    def default(path_to_file):
        return open(path_to_file, "r").read()[1]

    @staticmethod
    def execute_file(command, path_to_file, args=""):
        args_encapsulated = '"' + args + '"'
        args_encapsulated.replace("\r", " ")
        return os.popen(f"{command} {path_to_file} {args_encapsulated}").read()