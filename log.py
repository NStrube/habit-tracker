LogFile = open("Log", "w")

def log(s: str):
    """
    A helper method for logging to a file.
    """
    global LogFile
    LogFile.write(s + '\n')
