from bs4 import BeautifulSoup
from exceptions import ParserFindTagException, RequestException

from constants import RESPONSE_UTILS_PHRASE, TAG_ERROR_PHRASE


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = "utf-8"
        return response
    except RequestException:
        raise ConnectionError(
            RESPONSE_UTILS_PHRASE.format(url),
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        raise ParserFindTagException(TAG_ERROR_PHRASE.format(tag, attrs))
    return searched_tag


def make_soup(session, url):
    return BeautifulSoup(get_response(session, url).text, features="lxml")
