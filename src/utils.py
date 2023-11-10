from bs4 import BeautifulSoup
from exceptions import ParserFindTagException
from requests import RequestException

from constants import RESPONSE_UTILS_PHRASE, TAG_ERROR_PHRASE


def get_response(session, url, encoding="utf-8"):
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException as error:
        raise ConnectionError(
            RESPONSE_UTILS_PHRASE.format(url, error),
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        raise ParserFindTagException(TAG_ERROR_PHRASE.format(tag, attrs))
    return searched_tag


def make_soup(session, url, features="lxml"):
    return BeautifulSoup(get_response(session, url).text, features)
