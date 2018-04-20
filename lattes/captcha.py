"""
Module responsible to solve the captcha inside an image.
"""
from operator import itemgetter
from PIL import ImageChops
from PIL import Image
from pathlib import Path
import glob
import os
import re


class Captcha:

    """This class is responsible to solve a given image captcha."""
    symbols_folder = 'captcha_symbols'
    path = Path(__file__).parent.absolute()
    symbols_path = Path(os.path.join(path, symbols_folder))

    def __init__(self, captchaFile):
        """Given an image path, it tries to solve the captcha inside it."""
        self.code = None
        self.captcha = captchaFile
        self.image = Image.open(captchaFile)
        self.image = self.image.convert('RGB')
        self.symbols = self._get_symbols()
        self.black_white()
        self.crop()
        self.crack()
        self.image.close()

    def black_white(self):
        """Process the image by changing all the white pixels into black, and
        all the non-white into white."""
        width, height = self.image.size
        pixels = self.image.load()
        for x in range(0, width):
            for y in range(0, height):
                if pixels[x, y] == (255, 255, 255):
                    self.image.putpixel((x, y), (0, 0, 0))
                else:
                    self.image.putpixel((x, y), (255, 255, 255))

    def crop(self):
        """Crop all the waste of white in the black and white image."""
        width, height = self.image.size
        x_left_edge = self._get_left_white_edge()
        x_right_edge = self._get_right_white_edge()
        self.image = self.image.crop((x_left_edge, 0, x_right_edge, height))

    def _get_left_white_edge(self):
        """Get the boarderline top left pixel, in order to crop the image."""
        width, height = self.image.size
        pixels = self.image.load()
        for x in range(0, width):
            for y in range(0, height):
                if pixels[x, y] == (0, 0, 0):
                    return x - 1

    def _get_right_white_edge(self):
        """Get the boarderline bottom right pixel, in order to crop the
        image."""
        width, height = self.image.size
        pixels = self.image.load()
        for x in range(width-1, 0, -1):
            for y in range(height-1, 0, -1):
                if pixels[x, y] == (0, 0, 0):
                    return x + 2

    def _get_symbols(self):
        """Returns a symbol 'dictionary'. A list with tuple(symbol,image)."""
        pattern = '{}/(?P<symbol>[0-9a-z])'.format(self.symbols_folder)
        regex = re.compile(pattern)
        symbol_list = []
        symbols_paths = self.symbols_path.glob('*.png')
        symbols_paths = [path.absolute().as_posix() for path in symbols_paths]
        for symbol_file in symbols_paths:
            image = Image.open(symbol_file).convert(mode='RGB')
            symbol = regex.search(symbol_file).group('symbol')
            symbol_list.append((symbol, image))
        return symbol_list

    def match(self, img1, img2):
        """Compare 2 images and returns True or False."""
        if ImageChops.difference(img1, img2).getbbox() is None:
            return True
        else:
            return False

    def crack(self):
        """Iterate over the symbol library trying to match symbols."""
        temp_image = self.captcha[:-4] + '_crack' + '.png'
        self.image.save(temp_image)
        height = self.image.height
        characters = []
        for symbol in self.symbols:
            for x in range(0, self.image.width - symbol[1].width + 1, 1):
                box = (x, 0, x + symbol[1].width, height)
                cropped_img = self.image.crop(box)
                if self.match(symbol[1], cropped_img) is True:
                    characters.append((symbol[0], x))
                    break
        characters = sorted(characters, key=itemgetter(1))
        self.characters = characters
        for temp in glob.glob(temp_image):
            os.remove(temp)

    def get_text(self):
        """Return a captcha code."""
        self.code = ''
        for char in self.characters:
            self.code = self.code + char[0]
        return self.code
