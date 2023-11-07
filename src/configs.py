import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import (
    PRETTY_ARGUMENT,
    FILE_ARGUMENT,
    LOG_DIR_PATH,
    LOG_NAME,
)


LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = "%d.%m.%Y %H:%M:%S"


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(description="Парсер документации Python")
    parser.add_argument(
        "mode", choices=available_modes, help="Режимы работы парсера"
    )
    parser.add_argument(
        "-c", "--clear-cache", action="store_true", help="Очистка кеша"
    )
    parser.add_argument(
        "-o",
        "--output",
        choices=(PRETTY_ARGUMENT, FILE_ARGUMENT),
        help="Дополнительные способы вывода данных",
    )

    return parser


def configure_logging():
    log_dir = LOG_DIR_PATH
    log_dir.mkdir(exist_ok=True)
    log_file = LOG_NAME
    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=10**6, backupCount=5, encoding="utf-8"
    )
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler()),
    )
