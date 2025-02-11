import logging
import sys
import time
from logging.handlers import RotatingFileHandler
from colorlog import ColoredFormatter

def setup_logger(logfile="bot.log", level=logging.DEBUG):
    """Sets up the logging format with colors, timestamps, and rotation."""

    # Prevent multiple handlers from being added
    if len(logging.getLogger("SolanaBot").handlers) > 0:
        return logging.getLogger("SolanaBot")

    log_formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red'
        }
    )

    # File logging with rotation
    file_handler = RotatingFileHandler(logfile, maxBytes=5*1024*1024, backupCount=2)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    file_handler.setLevel(logging.DEBUG)

    # Console logging with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.DEBUG)

    # Setup logger
    logger = logging.getLogger("SolanaBot")
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

logger = setup_logger()

