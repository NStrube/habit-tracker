LogFile = open("Log", "w")

def log(s: str):
    global LogFile
    LogFile.write(s + '\n')
