from collections import defaultdict
import re
import logging
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    ANY_ERROR_PHRASE,
    CONSOLE_ARGUMENTS_PHRASE,
    DOWNLOADS_DIR,
    DOWNLOAD_LOGGING_PHRASE,
    EXPECTED_STATUS,
    KEY_ERROR_PHRASE,
    MAIN_DOC_URL,
    PEPS_URL,
    RESPONSE_ERROR_LOGGING_PHRASE,
    STATUS_ERROR_PHRASE,
)
from outputs import control_output
from utils import find_tag, get_response, make_soup


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, "whatsnew/")
    response = get_response(session, whats_new_url)
    results = [("Ссылка на статью", "Заголовок", "Редактор, Автор")]
    if response is None:
        return
    for section in tqdm(
        make_soup(session, whats_new_url)
        .select_one("#what-s-new-in-python div.toctree-wrapper")
        .select("li.toctree-l1")
    ):
        version_a_tag = section.find("a")
        href = version_a_tag["href"]
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            logging.error(RESPONSE_ERROR_LOGGING_PHRASE)
            continue
        soup = make_soup(session, version_link)
        h1 = find_tag(soup, "h1")
        dl = find_tag(soup, "dl")
        dl_text = dl.text.replace("\n", " ")
        results.append((version_link, h1.text, dl_text))
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = make_soup(session, MAIN_DOC_URL)

    sidebar = find_tag(soup, "div", attrs={"class": "sphinxsidebarwrapper"})
    ul_tags = sidebar.find_all("ul")
    for ul in ul_tags:
        if "All versions" in ul.text:
            a_tags = ul.find_all("a")
            break
    else:
        raise KeyError(KEY_ERROR_PHRASE)

    results = [("Ссылка на документацию", "Версия", "Статус")]
    pattern = r"Python (?P<version>\d\.\d+) \((?P<status>.*)\)"
    for a_tag in a_tags:
        link = a_tag["href"]
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ""
        results.append((link, version, status))
        return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, "download.html")
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = make_soup(session, downloads_url)
    table_tag = find_tag(soup, "table", {"class": "docutils"})
    pdf_a4_tag = find_tag(
        table_tag, "a", {"href": re.compile(r".+pdf-a4\.zip$")}
    )
    pdf_a4_link = pdf_a4_tag["href"]
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split("/")[-1]
    DOWNLOADS_DIR.mkdir(exist_ok=True)
    archive_path = DOWNLOADS_DIR / filename
    response = session.get(archive_url)
    with open(archive_path, "wb") as file:
        file.write(response.content)
    logging.info(DOWNLOAD_LOGGING_PHRASE.format(archive_path))


def pep(session):
    peps = defaultdict(int)
    response = get_response(session, PEPS_URL)
    if response is None:
        return
    soup = make_soup(session, PEPS_URL)
    section_tag = find_tag(soup, "section", {"id": "numerical-index"})
    tr_tags = section_tag.find_all("tr")

    for tr_tag in tqdm(tr_tags[1:]):
        first_column_tag = find_tag(tr_tag, "td")
        table_status = first_column_tag.text[1:]
        href = find_tag(tr_tag, "a")["href"]
        pep_url = urljoin(PEPS_URL, href)
        if get_response(session, pep_url) is None:
            logging.error(RESPONSE_ERROR_LOGGING_PHRASE)
            return
        peps_soup = make_soup(session, pep_url)
        dl_tag = find_tag(peps_soup, "dl")
        dt_tags = dl_tag.find_all("dt")
        for dt in dt_tags:
            if dt.text == "Status:":
                dt_status = dt
                break
        peps_status = dt_status.find_next_sibling("dd").string
        peps[peps_status] += 1
        if peps_status not in EXPECTED_STATUS[table_status]:
            error_info = STATUS_ERROR_PHRASE.format(
                pep_url, peps_status, EXPECTED_STATUS[table_status]
            )
            logging.info(error_info)
    return [
        ("Статус", "Количество"),
        *peps.items(),
        ("Всего", sum(peps.values())),
    ]


MODE_TO_FUNCTION = {
    "whats-new": whats_new,
    "latest-versions": latest_versions,
    "download": download,
    "pep": pep,
}


def main():
    configure_logging()
    logging.info("Парсер запущен!")
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(CONSOLE_ARGUMENTS_PHRASE.format(args))
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()

        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)

        if results is not None:
            control_output(results, args)

    except Exception as error:
        logging.exception(
            ANY_ERROR_PHRASE.format(error=error), stack_info=True
        )

    logging.info("Парсер завершил работу.")


if __name__ == "__main__":
    main()
