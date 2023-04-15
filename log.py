"""Provides a log method for debugging."""
def log(string: str):
    """
    A helper method for logging to a file.
    """
    with open("Log", "w") as log_file:
        log_file.write(string + '\n')
