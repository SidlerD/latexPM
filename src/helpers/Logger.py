import logging
import sys

def make_logger(name: str = "default", logging_level = logging.INFO):
    logger = logging.getLogger(name)
    if logger.handlers: # Logger already existed
        logger.handlers = []

    logger.setLevel(logging_level)  # Set the desired log level
    logger.propagate = 0

    # Create a StreamHandler to write logs to stdout
    stream_handler = logging.StreamHandler(sys.stdout)

    # Set the log level for the handler
    stream_handler.setLevel(logging_level)

    # Use custom format for log-messages: Don't show name of logger
    format_string = '%(asctime)s - %(levelname)-8s - %(message)s'
    # Only show time, no dates in message
    formatter = logging.Formatter(format_string, '%H:%M:%S')
    stream_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(stream_handler)

    return logger