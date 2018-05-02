from multiprocessing import current_process
from requests import Session, Request
from bs4 import BeautifulSoup as bs4
from lattes.config import BaseLogger
from lattes.captcha import Captcha
from pathlib import Path
import re
import os

logger_file = 'downloader_log.txt'


class Base(BaseLogger):

    max_tries = 50  # constant in order to give up on this curriculum.
    path = Path(__file__).parent.parent.absolute()
    domain_url = 'http://buscatextual.cnpq.br/buscatextual'
    get_capthca_url = domain_url + '/servlet/captcha?metodo=getImagemCaptcha'
    solve_captcha_url = domain_url + '/servlet/captcha?informado={}'\
                                     '&metodo=validaCaptcha'

    def __init__(self):
        """Base initializer for subclasses

        @attr domain:      Domain part of the url to be used for all requests
        @attr routes:      Dict of url routes the application uses.
                           The keys are the route_names and the values are the
                           routes.
        @attr urls:        Dict of urls to be used. A url consists of a domain
                           plus a route.
        @attr captcha:     A filename to be used to save captcha files,
                           This should be unique enough that multiprocesses
                           don't overlap files from different istnances.
        """
        super().__init__(rotating_file=logger_file)
        captcha = 'captcha_{}.png'.format(current_process().name)
        self.captcha_file = os.path.join(self.path, captcha)
        self.requests = {}
        self.requests['get_captcha'] = Request('GET', self.get_capthca_url)

    @classmethod
    def check_param(self, param, pattern):
        error_msg = 'ParamError: Expected a {} string as param.'
        try:
            match = re.match(pattern, param)
        except TypeError:
            raise TypeError(error_msg.format(error_msg))
        else:
            if match:
                return param
            else:
                raise ValueError(error_msg.format(error_msg))

    def read_captcha(self, session):
        """Given a session, gets a captcha and reads it into text.

        @param session:  Emulates a browsing session to be used for future
                         requests and posts preserving the session data.
        @type  session: requests.Session()

        @return: True or False, if the captcha was read successifuly or not.
        @rtype : bool
        """
        try:
            prepped = session.prepare_request(self.requests['get_captcha'])
            response = session.send(prepped)
        except Exception as e:
            self.logger.info('Error getting: {}.\n Error: {}'.format(
                             self.get_capthca_url, e))
            return False
        if response.status_code == 200:
            with open(self.captcha_file, 'wb') as captcha:
                captcha.write(response.content)
            code = Captcha(self.captcha_file).get_text()
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
        try:
            url = self.solve_captcha_url.format(code)
            self.requests['solve_captcha'] = Request('GET', url)
            prepped = session.prepare_request(self.requests['solve_captcha'])
            response = session.send(prepped)
        except Exception as e:
            self.logger.info('Error getting: {}.\n Error: {}'.format(
                             self.urls['solve_captcha'], e))
            return False
        if 'sucesso' in response.text:
            self.logger.info('Capthca authenticated')
            return True
        else:
            self.logger.info('Captcha not authenticated')
            return False


class Curriculum(Base):
    """Represents a curriculum vizualization page in which given a short_id
    for its initializer then long_id() makes it possible to enter the webpage
    in order to get the long_id necessery for downloadeing the xml version of
    the curriculum.
    """

    title = 'Currículo do Sistema de Currículos Lattes'
    post_url = Base.domain_url + '/visualizacv.do'

    def __init__(self, short_id):
        """Instance initializer.

        @param short_id: 10 character string that represents a curriculum id
                         for this webpage
        @type  short_id: str

        @attr _long_id : Curriculum 16 digits long id given by CNPQ.
                         Or False if couldnt get the long_id.
        @attr is_loaded: If page was successfully is_loaded or not: True or
                         False
        @attr response : Final http response object.
        @attr source   : Page source code.
        @attr soup     : Bs4 soup from page source code
        """

        super().__init__()
        self.short_id = self.check_param(short_id, '^[0-9A-Z]{10}$')
        self._long_id = None
        self.response = None
        self.source = None
        self.soup = None
        payload = {
            'metodo': (None, 'captchaValido'),
            'id': (None, self.short_id),
            'idiomaExibicao': (None, ''),
            'tipo': (None, ''),
            'informado': (None, '')
            }
        self.requests['post'] = Request('POST', self.post_url, data=payload)
        self.is_loaded = self.load()

    def __bool__(self):
        """Truthness of instance. If self.load() was successful"""
        return bool(self.is_loaded)

    def load(self):
        """Through requests.Session: makes a series of requests emulating a
        browser session in order to get inside the Curriculum page given a
        short_id

        @return:  Returns True and save a response object in self.response if
                  successfull or False if not
        @rtype :  bool
        """
        tries, curriculum = 0, False
        while not self.is_curriculum(curriculum) or tries < self.max_tries:
            tries += 1
            with Session() as session:
                self.logger.info('Starting try n:{} for {}'.format(
                                 tries, self.short_id))
                code = self.read_captcha(session)
                if code:
                    if self.solve_captcha(session, code):
                        try:
                            request = self.requests['post']
                            prepped = session.prepare_request(request)
                            curriculum = session.send(prepped)
                        except Exception as e:
                            self.logger.info(' POST Error: {}'.format(e))
                            continue
                        if self.is_curriculum(curriculum):
                            self.response = curriculum
                            return True
                        else:
                            self.logger.info('Error finding curriculum page')
                            continue
                    else:
                        self.logger.info('Error solving capthca.')
                        continue
                else:
                    self.logger.info('Error reading code: {}'.format(code))
                    continue
        self.logger.info('Could not accquire long_id in {} tries'.format(
                         self.max_tries))
        return False

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
            self.logger.info('Bool, not response')
            return False
        else:
            soup = bs4(response.text, 'lxml')
            if self.title in soup.title.text:
                self.response = response
                self.source = response.text
                self.soup = soup
                self.logger.info('Yes, yes!')
                return True
            else:
                self.logger.info('No, it is not!')
                return False

    @property
    def long_id(self):
        """Property for returning a long_id"""
        regex = re.compile('\d{16}')
        long_id = self.soup.find(href=regex)['href'][-16:]
        self.logger.info('long_id: {} | response: {}'.format(
                         long_id, self.response))
        self._long_id = long_id
        return self._long_id

    @property
    def date(self):
        last_updated = Preview.date(self.short_id)
        return last_updated


class Xml(Base):

    url = Base.domain_url + '/download.do'

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
        self.long_id = self.check_param(long_id, '^\d{16}$')
        self.file_name = None
        self.file_path = None
        self.check_path(output_dir)
        payload = {
            'metodo': (None, 'captchaValido'),
            'idcnpq': (None, self.long_id),
            'informado': (None, ''),
            }
        self.requests['post'] = Request('POST', self.url, data=payload)
        self.logger.info('Initializing XmlPage: {}'.format(self.long_id))
        self.is_downloaded = self.download_xml()

    def __bool__(self):
        """Truthness of instance, if file was downloaded."""
        return bool(self.is_downloaded)

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

    def download_xml(self):
        """Tries to download the xml.zip file associated with long_id

        @return:  True or False depending if download was sucessful or not
        @rtype :  bool
        """
        tries = 0
        while not self.file_path.exists() and tries < self.max_tries:
            tries += 1
            with Session() as session:
                self.logger.info('Starting Session(): {} try'.format(tries))
                code = self.read_captcha(session)
                if code:
                    if self.solve_captcha(session, code):
                        self.logger.info('Downloading xml...')
                        request = self.requests['post']
                        prepped = session.prepare_request(request)
                        response = session.send(prepped)
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
            return True
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


class Preview(Base):
    """Represents the vizualization page where one can get the update date
    without needing captchas."""

    url = ('http://buscatextual.cnpq.br/buscatextual'
           '/preview.do?metodo=apresentar&id=')
    logger = BaseLogger.from_file(Base.base_name, logger_file)

    @classmethod
    def date(cls, short_id):
        """Given a short id, open the Preview page and retrieves the date when
        the curriculum was last updated.
        Returns String with the last update or Flase if string date could not
        be retrieved.
        """
        short_id = cls.check_param(short_id, '^[A-Z0-9]{10}$')
        url = cls.url + short_id
        request = Request('GET', url).prepare()
        response = False
        tries = 0
        cls.logger.info('Getting upDATE for {}'.format(short_id))
        while not response or tries < cls.max_tries:
            tries += 1
            cls.logger.info('Try: {}'.format(tries))
            try:
                with Session() as session:
                    response = session.send(request)
            except Exception as e:
                cls.logger.info('Error: {}'.format(e))
                continue
            if response.ok:
                pattern = '(\d{2}/){2}\d{4}'
                regex = re.compile(pattern)
                soup = bs4(response.text, 'html.parser')
                date_text = soup.span.text
                date_text = regex.search(date_text).group()
                cls.logger.info('Response.ok: date: {}'.format(date_text))
                return date_text
            else:
                continue
        return False
