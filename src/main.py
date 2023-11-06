import re
import logging
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEPS_URL
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, "whatsnew/")
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features="lxml")
    main_div = find_tag(soup, "section", attrs={"id": "what-s-new-in-python"})
    div_with_ul = find_tag(main_div, "div", attrs={"class": "toctree-wrapper"})
    sections_by_python = div_with_ul.find_all(
        "li", attrs={"class": "toctree-l1"}
    )
    results = [("Ссылка на статью", "Заголовок", "Редактор, Автор")]

    for section in tqdm(sections_by_python):
        version_a_tag = section.find("a")
        href = version_a_tag["href"]
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features="lxml")
        h1 = find_tag(soup, "h1")
        dl = find_tag(soup, "dl")
        dl_text = dl.text.replace("\n", " ")
        results.append((version_link, h1.text, dl_text))
        return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features="lxml")

    sidebar = find_tag(soup, "div", attrs={"class": "sphinxsidebarwrapper"})
    ul_tags = sidebar.find_all("ul")
    for ul in ul_tags:
        if "All versions" in ul.text:
            a_tags = ul.find_all("a")
            break
    else:
        raise Exception("Ничего не нашлось")

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
    soup = BeautifulSoup(response.text, features="lxml")
    main_tag = find_tag(soup, "div", {"role": "main"})
    table_tag = main_tag.find_tag(soup, "table", {"class": "docutils"})
    pdf_a4_tag = table_tag.find_tag(
        soup, "a", {"href": re.compile(r".+pdf-a4\.zip$")}
    )
    pdf_a4_link = pdf_a4_tag["href"]
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split("/")[-1]
    downloads_dir = BASE_DIR / "downloads"
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, "wb") as file:
        file.write(response.content)
    logging.info(f"Архив был загружен и сохранён: {archive_path}")


def pep(session):
    peps = {}
    response = get_response(session, PEPS_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features="lxml")
    section_tag = find_tag(soup, "section", {"id": "numerical-index"})
    tr_tags = section_tag.find_all("tr")
    results = [("Статус", "Количество")]

    for tr_tag in tqdm(tr_tags[1:]):
        first_column_tag = find_tag(tr_tag, "td")
        table_status = first_column_tag.text[1:]
        href = find_tag(tr_tag, "a")["href"]
        pep_url = urljoin(PEPS_URL, href)
        peps_response = get_response(session, pep_url)
        if peps_response is None:
            return
        peps_soup = BeautifulSoup(peps_response.text, features="lxml")
        dl_tag = find_tag(peps_soup, "dl")
        dt_tags = dl_tag.find_all("dt")
        for dt in dt_tags:
            if dt.text == "Status:":
                dt_status = dt
                break
        peps_status = dt_status.find_next_sibling("dd").string
        status_counter = peps.get(peps_status) or 0
        peps[peps_status] = status_counter + 1
        if peps_status not in EXPECTED_STATUS[table_status]:
            logging.info(
                f"Несовпадающие статусы:\n"
                f"{pep_url}\n"
                f"Статус в карточке: {peps_status}\n"
                f"Ожидаемые статусы: {EXPECTED_STATUS[table_status]}"
            )
        for item in peps.items():
            results.append(item)
            results.append(("Total", len(tr_tags[1:])))
        return results


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
    logging.info(f"Аргументы командной строки: {args}")

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)

    logging.info("Парсер завершил работу.")


if __name__ == "__main__":
    main()
