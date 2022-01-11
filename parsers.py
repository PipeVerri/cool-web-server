import os  # for rendering the php

extensionCommand = {"php": "php", "py": "python"}


def default(path_to_file):
    return open(path_to_file, "r").read()[1]


def execute_file(command, path_to_file, args=""):
    args_encapsulated = '"' + args + '"'
    args_encapsulated.replace("\r", " ")
    return os.popen(f"{command} {path_to_file} {args_encapsulated}").read()
