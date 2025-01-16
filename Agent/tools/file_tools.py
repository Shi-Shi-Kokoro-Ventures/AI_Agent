# agent/tools/file_tools.py

import os

def read_file(file_path: str) -> str:
    """
    Reads the entire contents of a file and returns as a string.
    """
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' does not exist."
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(file_path: str, content: str) -> str:
    """
    Writes content to a file, overwriting if it already exists.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File '{file_path}' written successfully."
