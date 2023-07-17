import logging
import sys

def make_logger(name: str = "default"):
    logger = logging.getLogger(name)
    if logger.handlers: # Logger already existed
        return logger
    logger.setLevel(logging.INFO)  # Set the desired log level
    logger.propagate = 0

    # Create a StreamHandler to write logs to stdout
    stream_handler = logging.StreamHandler(sys.stdout)

    # Optionally, you can set the log level for the handler
    stream_handler.setLevel(logging.DEBUG)

    # Optionally, customize the log format for the handler
    # format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    format_string = '%(asctime)s - %(levelname)-8s - %(message)s'
    formatter = logging.Formatter(format_string, '%H:%M:%S')
    stream_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(stream_handler)

    return logger