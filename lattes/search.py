#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lattes.search_data import search_data, params_payload
from bs4 import BeautifulSoup as bs4
from lattes.config import BaseLogger
import requests
import re


class Base(BaseLogger):
    """BaseClass for sharing data and applying logger in module classes."""

    url = 'http://buscatextual.cnpq.br/buscatextual/busca.do?'

    def __init__(self):
        super().__init__(rotating_file='log_scraper.txt')


class Search(Base):
    """Represent a search session with the '.' as search parameter."""
    url = 'http://buscatextual.cnpq.br/buscatextual/busca.do?'

    def __init__(self):
        """Initializes instance, craft search request and send it away for
        result.

        @attr query: '.' for searching the entire database.
        @attr search_data: The POST data to be used in the query.
        @attr session: The requests.Session of the query.
        @attr ok: The truthness of the instance. If query_resposne.ok is True.
        """

        super().__init__()
        self.query = '.'
        self.search_data = search_data
        self.search_data['textoBusca'] = self.query
        self.session = requests.Session()
        self.ok = False
        self.logger.info('Searching for "." in {}'.format(self.url))
        try:
            self.query_resposne = self.session.post(self.url,
                                                    data=self.search_data)
            self.logger.info(
                'Search finished with {} results'.format(self.total))
        except Exception as e:
            self.logger.info('Could not query {}'.format(self.url))
            self.logger.info('Exception: {}'.format(e))
            raise e
        else:
            if self.query_resposne.ok:
                self.ok = True

    def __bool__(self):
        """Instance assertion."""
        return self.ok

    @property
    def total(self):
        """Total of results of a search session."""
        soup = bs4(self.query_resposne.text, 'html.parser')
        total = soup.find(class_='tit_form').b.text
        return int(total)


class Scraper(Base):
    """Represents a pagination Page, after the results in search, this page
    abstraction gives us the ability to load range of results."""

    @classmethod
    def from_registers(cls, search, reg_from, reg_to):
        """Given a search object and a range of resulting registers, load
        those registers in order to extract the respective short_ids.
        
        @param search  : A valid search Object to use it's session for
                         pagination.
        @param reg_from: Start register number for page to load from.
        @param reg_to  : Interval number for page to load register up to.
        """
        cls.logger.info('Loading pagination from register'
                        '{} to {}'.format(reg_from, reg_to))
        session = search.session
        payload = params_payload
        payload['registros'] = '{};{}'.format(reg_from, reg_to)
        response = cls.load_page(session, payload, reg_from, reg_to)
        if response.ok:
            soup = bs4(response.text, 'html.parser')
            if 'Busca Textual' in soup.title.text:
                cls.logger.info('Done.')
                return cls.extract_ids(soup)
            else:
                cls.logger.info('Wrong page: "Busca Textual" not in title')
                return False
        else:
            cls.logger.info('Wrong response getting pagination.')
            return False

    @classmethod
    def load_page(cls, session, payload, reg_from, reg_to):
        """Tries multiple times to load the page in order to prevent some
        connection errors.
        
        @param session : requests.Session to be used to load the next page.
        @param payload : Params to be used for the session.get.
        @param reg_from: Start register number for page to load from.
        @param reg_to  : Interval number for page to load register up to.

        @return        : Page request response or False depending if the
                         requests was successful or not.
        @rtype         : requests.response or False
        """

        response, tries, max_tries = False, 0, 50
        while not response and tries < max_tries:
            tries += 1
            try:
                response = session.get(cls.url, params=payload)
                cls.info('Pagination request sent.')
            except:
                continue
            else:
                if response.ok:
                    return response
                else:
                    return False
        else:
            return False

    @classmethod
    def extract_ids(cls, soup):
        """Given a soup object, extract and returns the short_ids inside it.
        @param soup: A ready to be parsed html source code.
        @type  soup: BeautifulSoup()

        @return: List of short_ids found in soup.
        @rtype : list of str
        """
        cls.logger.info('Extracting ids...')
        pattern = '[A-Z0-9]{10}'
        regex = re.compile(pattern)
        anchors = soup.find_all('a', href=regex)
        hrefs = (anchor['href'] for anchor in anchors)
        short_ids = [regex.search(href).group() for href in hrefs]
        cls.logger.info('{} short_ids extracted'.format(len(short_ids)))
        return short_ids
