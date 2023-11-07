import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (
    DATETIME_FORMAT,
    PRETTY_ARGUMENT,
    FILE_ARGUMENT,
    RESULTS_DIR,
    SAVING_LOGGING_PHRASE,
)


def default_output(results, *args):
    for row in results:
        print(*row)


def pretty_output(results):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = "l"
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    RESULTS_DIR.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now_formatted = dt.datetime.now().strftime(DATETIME_FORMAT)
    file_name = f"{parser_mode}_{now_formatted}.csv"
    file_path = RESULTS_DIR / file_name
    with open(file_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f, dialect=csv.unix_dialect)
        writer.writerows(results)
    logging.info(SAVING_LOGGING_PHRASE.format(file_path))


TYPES_OF_OUTPUT = {
    PRETTY_ARGUMENT: pretty_output,
    FILE_ARGUMENT: file_output,
    None: default_output,
}


def control_output(results, cli_args):
    TYPES_OF_OUTPUT.get(cli_args.output)(results, cli_args)
