from collections import defaultdict
from urllib.parse import urljoin
import re
import logging


import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    ANY_ERROR,
    BASE_DIR,
    CONSOLE_ARGUMENTS,
    DOWNLOAD_LOGGING,
    DOWNLOADS_NAME,
    DL_ERROR,
    EXPECTED_STATUS,
    RESPONSE_ERROR_LOGGING,
    FINAL_LOGGING,
    LATEST_VERSIONS_ERROR,
    MAIN_DOC_URL,
    PEPS_URL,
    START_LOGGING,
    STATUS_ERROR,
)
from outputs import control_output
from utils import find_tag, make_soup


def whats_new(session):
    results = [("Ссылка на статью", "Заголовок", "Редактор, Автор")]
    logs = []
    for version_a_tag in tqdm(
        make_soup(session, urljoin(MAIN_DOC_URL, "whatsnew/")).select(
            "#what-s-new-in-python div.toctree-wrapper.compound "
            "li.toctree-l1 a[href$='.html']"
        )
    ):
        href = version_a_tag["href"]
        version_link = urljoin(urljoin(MAIN_DOC_URL, "whatsnew"), href)
        try:
            soup = make_soup(session, version_link)
            h1 = find_tag(soup, "h1")
            dl = find_tag(soup, "dl")
            if dl is not None:
                dl_text = dl.text.replace("\n", " ")
            else:
                dl_text = DL_ERROR
            results.append((version_link, h1.text, dl_text))
        except Exception as error:
            logs.append(RESPONSE_ERROR_LOGGING.format(
                version_link, error))
    list(map(logging.error, logs))
    return results


def latest_versions(session):
    soup = make_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, "div", attrs={"class": "sphinxsidebarwrapper"})
    ul_tags = sidebar.find_all("ul")
    for ul in ul_tags:
        if "All versions" in ul.text:
            a_tags = ul.find_all("a")
            break
        else:
            raise ValueError(LATEST_VERSIONS_ERROR)

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
    soup = make_soup(session, downloads_url)
    table_tag = find_tag(soup, "table", {"class": "docutils"})
    pdf_a4_tag = find_tag(
        table_tag, "a", {"href": re.compile(r".+pdf-a4\.zip$")})
    pdf_a4_link = pdf_a4_tag["href"]
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split("/")[-1]
    DOWNLOADS_DIR = BASE_DIR / DOWNLOADS_NAME
    DOWNLOADS_DIR.mkdir(exist_ok=True)
    archive_path = DOWNLOADS_DIR / filename
    response = session.get(archive_url)
    with open(archive_path, "wb") as file:
        file.write(response.content)
    logging.info(DOWNLOAD_LOGGING.format(archive_path))


def pep(session):
    peps = defaultdict(int)
    soup = make_soup(session, PEPS_URL)
    logs = []
    status_logs = []
    section_tag = find_tag(soup, "section", {"id": "numerical-index"})
    tr_tags = section_tag.find_all("tr")

    for tr_tag in tqdm(tr_tags[1:]):
        first_column_tag = find_tag(tr_tag, "td")
        table_status = first_column_tag.text[1:]
        href = find_tag(tr_tag, "a")["href"]
        pep_url = urljoin(PEPS_URL, href)
        try:
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
                status_logs.append(STATUS_ERROR.format(
                    pep_url, peps_status, EXPECTED_STATUS[table_status]
                ))
        except Exception as error:
            logs.append(RESPONSE_ERROR_LOGGING.format(pep_url, error))
    list(map(logging.info, status_logs))
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
    logging.info(START_LOGGING)
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(CONSOLE_ARGUMENTS.format(args))
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)

        if results is not None:
            control_output(results, args)

    except Exception as error:
        logging.exception(ANY_ERROR.format(
            error=error), stack_info=True)

    logging.info(FINAL_LOGGING)


if __name__ == "__main__":
    main()
