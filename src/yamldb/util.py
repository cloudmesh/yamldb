"""A small set of utility functions for file operations."""


def readfile(filename, mode="r"):
    """Reads the content of a file.

    Args:
        filename (str): The filename.
        mode (str): The file mode. Default is 'r'.

    Returns:
        str: The content of the file.

    Raises:
        ValueError: If an incorrect mode is provided.
    """
    if mode not in ["r", "rb"]:
        raise ValueError(f"Incorrect mode: expected 'r' or 'rb', given {mode}")

    with open(filename, mode) as file:
        content = file.read()
    return content


def writefile(filename, content):
    """
    Writes the content into the file.

    Args:
        filename (str): The filename.
        content (str): The content to be written.

    Returns:
        None
    """
    with open(filename, "w") as outfile:
        outfile.write(content)
        outfile.truncate()
