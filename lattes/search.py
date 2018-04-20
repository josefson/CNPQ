from search_data import search_data, params_payload
from bs4 import BeautifulSoup as bs4
from lattes.config import BaseLogger
import requests


class SearchSession:
    url = 'http://buscatextual.cnpq.br/buscatextual/busca.do?'
    search_data = search_data

    def __init__(self, query='.'):
        self.search_data['textoBusca'] = query
        self.session = requests.Session()
        self.query_resposne = None
        try:
            self.query_resposne = self.session.post(self.url,
                                                    data=self.search_data)
        except requests.exceptions.Timeout as terror:
            pass
        except requests.exceptions.ConnectionError as cerror:
            pass
        except requests.exceptions.RequestException as rerror:
            pass
        except Exception as e:
            pass

    @property
    def total(self):
        soup = bs4(self.query_resposne.text, 'html.parser')
        total = soup.find(class_='tit_form').b.text
        return int(total)


class SearchScraper:

    url = 'http://buscatextual.cnpq.br/buscatextual/busca.do?'

    def __inti__(self, search_session, out_file='shortids', chunk_size=1000):
        self.session = search_session.session
        self.total = search_session.total
        self.chunk = chunk_size
        self.params = params_payload

    def harvest(self):
        for n in range(1, self.total, self.chunk):
            self.params['registros'] = '{};{}'.format(n, self.chunk)
            self.sesion.get(self.url, params=self.params)
