"""
A small set of utitlit functions, that we could also have gotten from
cloudmesh.common.
"""

def readfile(filename, mode='r'):
    """
    returns the content of a file
    :param filename: the filename
    :return:
    """
    if mode not in ['r', 'rb']:
        raise ValueError(f"incorrect mode : expected 'r' or 'rb' given {mode}")

    with open(filename, mode)as file:
        content = file.read()
        file.close()
    return content


def writefile(filename, content):
    """
    writes the content into the file
    :param filename: the filename
    :param content: teh content
    :return:
    """
    with open(filename, 'w') as outfile:
        outfile.write(content)
        outfile.truncate()
