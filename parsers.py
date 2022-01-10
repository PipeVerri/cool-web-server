import os  # for rendering the php


def render_default(path_to_file):
    return open(path_to_file, "r").read()


def render_php(path_to_file):
    return os.popen("php " + path_to_file).read()


def execute_file(command, path_to_file, request):
    return os.popen(f"{command} {path_to_file} {request}").read()
