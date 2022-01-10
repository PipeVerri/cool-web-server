import os  # for rendering the php

extensionCommand = {"php": "php", "py": "python"}


def default(path_to_file):
    return open(path_to_file, "r").read()


def execute_file(command, path_to_file, request=""):
    return os.popen(f"{command} {path_to_file} {request}").read()
