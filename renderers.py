import os  # for rendering the php


def default(path_to_file):
    return open(path_to_file, "r").read()


def php(path_to_file):
    return os.popen("php " + path_to_file).read()
