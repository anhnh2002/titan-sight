import logging
from typing import Union
from pathlib import Path
from logging import StreamHandler
from coloredlogs import ColoredFormatter


def setup_logging():
    logging.basicConfig(level=logging.DEBUG)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)


def get_logger(name: str, file: Union[str, Path]=None, stdout=True, level="info"):
    handlers = []
    FORMAT = "%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s"
    level = logging.getLevelName(level.upper())

    if stdout:
        formatter = ColoredFormatter(FORMAT)
        stdout_handler = StreamHandler()
        stdout_handler.setLevel(level)
        stdout_handler.setFormatter(formatter)
        handlers.append(stdout_handler)

    if file:
        if isinstance(file, str):
            file = Path(file)
        file.parent.mkdir(parents=True, exist_ok=True)
        formatter = logging.Formatter(FORMAT)
        file_handler = logging.FileHandler(file, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)  # Add this line
    for handler in handlers:
        logger.addHandler(handler)
    return logger

logger = get_logger("search-engine")