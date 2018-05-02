# CNPQ
Captcha Negated by Python reQuests - For the CNPq lattes database.

The Lattes curriculum database was supposed to be of public access according to federal laws, however its managers are denying public/free access by placing captchas to:
* Simply vizualize the curriculum
* Download the xml representation of the curriculum
Bear in mind that in order to download the xml one needs to vizualize the curriculum first. This implies that in order to download a single curriculum, one must solve 2 captchas.
    1. Loading the CurriculumPage.
    2. For Actually downloading the xml throuhg the link in the CurriculumPage.

I find this unacceptable.

Restrictions:
1. In order to get the xmls, we need long_ids: a [0-9]{16} string. This is only shown inside the the page where we can vizualize the curriculum page, therefore we will call this a CurriculumPage.
2. In order to go vizualize a curriculum page, we need a short_id: a [A-Z0-9]{10} string. This can be retrieved inside CNPQ's search system.
So, for example: This short_id: K4260007T6 is related to this long_id: 6380212729787758

Architecture:
As opposite to building a script, I'll just abstract away those webpages in order for others to consume those classes as they need:
*Curriculum class is a representation of the CurriculumPage. This class should be instantiated with a short_it as an argument. Its instance will try to solve the required captchas and get the correct page at the end. If you do not need the xml and the data inside this page is enough, you could subclass this page and write methods for retireving data from the class attributes(source or soup) whatever you are more confortable with.
*Xml class is a representation of the XmlPage(page responsible to download the actual xml). This class should be instantiated with a long_id and an output_directory for the downloaded files. Any instance of this class will then try to solve the required captchas and download the long_id related xml.zip file.

## Requirements
python 3

Python libraries necessary:
* requests
* BeautifulSoup
* Pillow

## Installation
It is recommended you use a python virtualenvironment.
```
$pip install virtualenvwrapper
$mkvirtualenv cnpq
$workon cnpq
```
Then run ```$which python``` and check for an output similar to this:
```
/Users/josefson/.virtualenvs/cnpq/bin/python
```
Only then install the python dependencies eiher through pip or pipenv:
```
$pip install -r requirements.txt
```
or
```
$pip install pipenv
$pipenv install
```

## Usage
First we install the package in the virtualenv:
```$pip install -e lattes```

Then we can use the library like this:
```
from lattes.pages import Curriculum, Xml
short_id = 'K4745447D6'
curriculum = Curriculum(short_id)
xml = Xml(curriculum.long_id, '~/xmls/')
```
As this is just a library, it's up the the client application to write the business logic.
However I'm adding a couple files as example on how to consume the lattes lib.

## Thanks
Special thanks to my friend Bruno Duarte that guided me in the way how images works and to my sponsors.

### Sponsors

*   Roney Fraga
*   Sheila Leite

[![PayPayl donate button](https://img.shields.io/badge/paypal-donate-yellow.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WA7DVSWHPZLBE "Donate to this project using Paypal")


## LICENSE
Copyright (c) 2015 Josefson Fraga Souza

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
