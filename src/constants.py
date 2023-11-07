from pathlib import Path

MAIN_DOC_URL = "https://docs.python.org/3/"
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = "%Y-%m-%d_%H-%M-%S"
EXPECTED_STATUS = {
    "A": ("Active", "Accepted"),
    "D": ("Deferred",),
    "F": ("Final",),
    "P": ("Provisional",),
    "R": ("Rejected",),
    "S": ("Superseded",),
    "W": ("Withdrawn",),
    "": ("Draft", "Active"),
}
PEPS_URL = "https://peps.python.org/"
PRETTY_ARGUMENT = "pretty"
FILE_ARGUMENT = "file"
LOG_DIR = "logs"
LOG_FILE = "parser.log"
RESULTS_NAME = "results"
DOWNLOADS_NAME = "downloads"
LOG_DIR_PATH = BASE_DIR / LOG_DIR
LOG_NAME = LOG_DIR / LOG_FILE
RESULTS_DIR = BASE_DIR / RESULTS_NAME
DOWNLOADS_DIR = BASE_DIR / DOWNLOADS_NAME
DOWNLOAD_LOGGING_PHRASE = "Архив был загружен и сохранён: {}"
RESPONSE_ERROR_LOGGING_PHRASE = "Ответ не получен"
KEY_ERROR_PHRASE = "Ничего не нашлось"
STATUS_ERROR_PHRASE = (
    "Несовпадающие статусы:\n"
    "{}\n"
    "Статус в карточке: {}\n"
    "Ожидаемые статусы: {}"
)
CONSOLE_ARGUMENTS_PHRASE = "Аргументы командной строки: {}"
ANY_ERROR_PHRASE = "Работа парсера завершилась с ошибкой: {}"
SAVING_LOGGING_PHRASE = "Файл с результатами был сохранён: {}"
RESPONSE_UTILS_PHRASE = "Возникла ошибка при загрузке страницы {}"
TAG_ERROR_PHRASE = "Не найден тег {} {}"
