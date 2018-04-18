from multiprocessing import current_process
from logging.config import fileConfig
from bs4 import BeautifulSoup as bs4
from captcha import Captcha
from pathlib import Path
import requests
import logging
import os
import re


CONFIG_LOGGER = 'logging_config.ini'


class Base:

    max_tries = 50  # constant in order to give up on this curriculum.

    def __init__(self):
        """Base initializer for subclasses

        @attr domain:      Domain part of the url to be used for all requests
        @attr routes:      Dict of url routes the application uses.
                           The keys are the route_names and the values are the
                           routes.
        @attr urls:        Dict of urls to be used. A url consists of a domain
                           plus a route.
        @attr id:          An id to be used as an unique identifier for names,
                           mainly the captcha filename which could be used over
                           the multiprocesses.
        @attr captcha_png: A filename to be used to save captcha files,
                           This should be unique enough that multiprocesses
                           don't overlap files from different istnances.
        """
        self.domain = 'http://buscatextual.cnpq.br/buscatextual'
        self.routes = {
            'get_captcha': '/servlet/captcha?metodo=getImagemCaptcha',
            'solve_captcha': '/servlet/captcha?informado={}&metodo=validaCaptcha',
            }
        self.urls = {
            'get_captcha': self.domain + self.routes['get_captcha'],
            'solve_captcha': self.domain + self.routes['solve_captcha'],
            }
        self.id = current_process().name
        self.logger = self.get_logger(self.id)
        self.captcha_png = 'captcha_{}.png'.format(self.id)

    def get_logger(self, name):
        """Create and returns a logger object configured based on an external
        file: CONFIG_LOGGER.
        """
        fileConfig(CONFIG_LOGGER)
        logger = logging.getLogger(name)
        return logger

    def read_captcha(self, session):
        """Given a session, gets a captcha and reads it into text.

        @param session:  Emulates a browsing session to be used for future
                         requests and posts preserving the session data.
        @type  session: requests.Session()

        @return: True or False, if the captcha was read successifuly or not.
        @rtype : bool
        """
        response = session.get(self.urls['get_captcha'])
        if response.status_code == 200:
            with open(self.captcha_png, 'wb') as captcha:
                captcha.write(response.content)
            code = Captcha(self.captcha_png).get_text()
            if len(code) == 4:
                self.logger.info('Read captcha: {}'.format(code))
                return code
            else:
                self.logger.info('Wrong captcha reading: {}'.format(code))
                return False
        else:
            self.logger.info('Status-code {}'.format(response.status_code))
            return False

    def solve_captcha(self, session, code):
        """Solves a captcha.

        @param session:  Emulates a browsing session to be used for future
                         requests and posts preserving the session data.
        @type  session: requests.Session()

        @return:  True or False depending if the captcha informed ended up in
                  a authenticated session or not.
        @rtype :  bool
        """
        response = session.get(self.urls['solve_captcha'].format(code))
        if 'sucesso' in response.text:
            self.logger.info('Capthca authenticated')
            return True
        else:
            self.logger.info('Captcha not authenticated')
            return False


class CurriculumPage(Base):
    """Represents a curriculum vizualization page in which given a short_id
    for its initializer then long_id() makes it possible to enter the webpage
    in order to get the long_id necessery for downloadeing the xml version of
    the curriculum.
    """
    regex = re.compile('\d{16}')

    def __init__(self, short_id):
        """Objeck initializer.

        @param short_id: 10 character string that represents a curriculum id
                         for this webpage
        @type  short_id: str

        @attr _long_id: Curriculum 16 digits long id given by CNPQ.
                        Or False if couldnt get the long_id.
        @attr files: Dict containing necessary data to be sent in final POST.
        """
        super().__init__()
        self.short_id = short_id
        self._long_id = None
        self.files = {'metodo': (None, 'captchaValido'),
                      'id': (None, self.short_id),
                      'idiomaExibicao': (None, ''),
                      'tipo': (None, ''),
                      'informado': (None, '')}
        self.urls['post'] = self.domain + '/visualizacv.do'

    def is_curriculum(self, response):
        """Verify if the response object is from a curriculum page.

        @param response: should be either a boolead, when called
        @type  :  boolean or response from requests

        @return:  True or False depending if response match curriculum page
        @rtype :  bool
        """
        self.logger.info('Is response a curriculum page?')
        if type(response) is bool:
            # Necessary for while response is False and it's not yet a response
            return False
        else:
            if self.find_long_id(response):
                self.logger.info('Yes, yes!')
                return True
            else:
                return False

    @property
    def long_id(self):
        """Through requests.Session: makes a series of requests emulating a
        browser session in order to get inside the Curriculum page given a
        short_id

        @return:  Return False in case of MAX_TRIES was reached, otherwise
                  returns a string containing the long_id.
        @rtype :  False or string
        """
        tries, curriculum = 0, False
        while not self.is_curriculum(curriculum) or tries < self.max_tries:
            tries += 1
            with requests.Session() as session:
                self.logger.info(
                    'Starting try n:{} for {}'.format(self.short_id, tries)
                    )
                code = self.read_captcha(session)
                if code:
                    if self.solve_captcha(session, code):
                        curriculum = session.post(self.urls['post'],
                                                  files=self.files)
                        if self.is_curriculum(curriculum):
                            self._long_id = self.find_long_id(curriculum)
                            return self._long_id
                        else:
                            self.logger.info('Trying again...')
                            continue
                    else:
                        self.logger.info('Trying again...')
                        continue
                else:
                    self.logger.info('Trying again...')
                    continue
        self.logger.info('Could not accquire long_id in {} tries'.format(
                         self.max_tries))
        return False

    def find_long_id(self, response):
        """Given a response retreives and returns a long_id."""
        soup = bs4(response.text, 'lxml')
        long_id = soup.find(href=self.regex)['href'][-16:]
        self.logger.info('long_id: {} | response: {}'.format(
                         long_id, response))
        return long_id


class CurriculumXml(Base):

    def __init__(self, long_id, output_dir):
        """ Instance initializer.

        @param long_id: Curriculum 16 digits long id given by CNPQ.
        @type  long_id: str

        @param output_dir: Full path where to save the related xml file.
        @type  output_dir: str

        @attr: files: Dict containing post data to be used on final POST.
        @attr: file_name: str containing absolute path + file name of xml.
        @attr: file_path: pathlib.Path() instance
        """
        super().__init__()
        self.long_id = long_id
        self.urls['post'] = self.domain + '/download.do'
        self.files = {
            'metodo': (None, 'captchaValido'),
            'idcnpq': (None, self.long_id),
            'informado': (None, ''),
            }
        self.file_name = None
        self.file_path = None
        self.check_path(output_dir)
        self.logger.info('Initializing XmlPage: {}'.format(self.long_id))

    def check_path(self, path):
        """Checks if given path exists and is a dir. In which case instantiate
        file_name and file_path attributes."""
        path = Path(path)
        if path.exists() and path.is_dir():
            xml_name = '{}.zip'.format(self.long_id)
            self.file_name = os.path.join(path.as_posix(), xml_name)
            self.file_path = Path(self.file_name)
            self.logger.info('Download path: {}'.format(
                             self.file_path.as_posix()))
        else:
            self.logger.info(
                'Provided path either does not exists or is not a directory: '
                '{}'.format(path.as_posix())
                )
            raise FileNotFoundError(
                '{} does not exists or is not a directory'.format(
                    path.as_posix())
                )

    def get_xml(self):
        """Tries to download the xml.zip file associated with long_id

        @return:  True or False depending if download was sucessful or not
        @rtype :  bool
        """
        tries = 0
        while not self.file_path.exists() and tries < self.max_tries:
            tries += 1
            with requests.Session() as session:
                self.logger.info('Starting Session(): {} try'.format(tries))
                code = self.read_captcha(session)
                if code:
                    if self.solve_captcha(session, code):
                        self.logger.info('Downloading xml...')
                        response = session.post(self.urls['post'],
                                                files=self.files)
                        if self.save_xml(response):
                            return True
                        else:
                            self.logger.info('Trying again...')
                            continue
                    else:
                        self.logger.info('Trying again...')
                        continue
                else:
                    self.logger.info('Trying again...')
                    continue
        if self.file_path.exists():
            self.logger.info('{} already downloaded'.format(self.file_name))
            return False
        else:
            self.logger.info('Max tries exceeded: {}'.format(tries))
            return False

    def save_xml(self, response):
        """Given a response object from a request, saves the zip file contained
        within the response.

        @return:  True or False depending on if the zip file was successifuly
                  retreived and saved.
        @rtype :  bool
        """
        if response.status_code == 200:
            self.logger.info('Post sucessful- status_code 200.')
            self.logger.info('Saving file...')
            with open(self.file_name, 'wb') as xml:
                xml.write(response.content)
            path = self.file_path
            if path.exists() and path.is_file():
                self.logger.info('File saved at {}'.format(path.as_posix()))
                return True
            else:
                self.logger.info('Could not save file at {}.'.format(
                                 path.as_posix()))
                return False
        else:
            return False
