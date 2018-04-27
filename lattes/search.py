#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lattes.search_data import search_data, params_payload
from bs4 import BeautifulSoup as bs4
from lattes.config import BaseLogger
import requests
import re


class Base(BaseLogger):

    url = 'http://buscatextual.cnpq.br/buscatextual/busca.do?'

    def __init__(self):
        super().__init__(rotating_file='scraper_log.txt')


class Search(Base):
    url = 'http://buscatextual.cnpq.br/buscatextual/busca.do?'

    def __init__(self):
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
            if self.query_resposne:
                self.ok = True

    @property
    def total(self):
        soup = bs4(self.query_resposne.text, 'html.parser')
        total = soup.find(class_='tit_form').b.text
        return int(total)


class Scraper(Base):

    @classmethod
    def from_registers(cls, search, reg_from, reg_to):
        session = search.session
        payload = params_payload
        payload['registros'] = '{};{}'.format(reg_from, reg_to)
        response = cls.load_page(session, payload, reg_from, reg_to)
        if response:
            soup = bs4(response.text, 'html.parser')
            if 'Busca Textual' in soup.title.text:
                return cls.extract_ids(soup)
            else:
                return False
        else:
            return False

    @classmethod
    def load_page(cls, session, payload, reg_from, reg_to):
        response, tries, max_tries = False, 0, 50
        while not response and tries < max_tries:
            tries += 1
            try:
                response = session.get(cls.url, params=payload)
            except:
                continue
            if response.ok:
                return response
            else:
                return False

    @classmethod
    def extract_ids(cls, soup):
        pattern = '[A-Z0-9]{10}'
        regex = re.compile(pattern)
        anchors = soup.find_all('a', href=regex)
        hrefs = (anchor['href'] for anchor in anchors)
        short_ids = [regex.search(href).group() for href in hrefs]
        return short_ids
