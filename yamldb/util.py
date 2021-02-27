def readfile(filename, mode='r'):
    """
    returns the content of a file
    :param filename: the filename
    :return:
    """
    if mode != 'r' and mode != 'rb':
        Console.error(f"incorrect mode : expected 'r' or 'rb' given {mode}")
    else:
        with open(path_expand(filename), mode)as f:
            content = f.read()
            f.close()
        return content


def writefile(filename, content):
    """
    writes the content into the file
    :param filename: the filename
    :param content: teh content
    :return:
    """
    with open(path_expand(filename), 'w') as outfile:
        outfile.write(content)
        outfile.truncate()
