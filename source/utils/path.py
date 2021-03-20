import os


def get_file_path(filename):
    return os.path.join(os.path.dirname(__file__), "../files", filename)
