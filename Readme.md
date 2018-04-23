# CNPQ
Captcha Negated by Python reQuests - For the CNPq lattes database.

The Lattes curriculum database was supposed to be of public access according to federal laws, however its managers are denying public/free access by placing captchas to:
* Simply vizualize the curriculum
* Download the xml representation of the curriculum
Bear in mind that in order to download the xml one needs to vizualize the curriculum first. This implies that in order to download a single curriculum, one must solve 2 captchas. I find this is unaceptable.

Restrictions:
1. In order to get the xmls, we need long_ids: a [0-9]{16} length string. This is only shown inside the the page where we can vizualize the curriculum page.
2. In order to go vizualize a curriculum page, we need a short_id: a [A-Z0-9]{10} length string. This can be retrieved inside CNPQ's search system.
So, for example: This short_id: K4260007T6 is related to this long_id: 6380212729787758
The problem was broken into 3 parts, which are necessary for getting the final result: a xml file.

Architecture:
As opposite to building a script, I'll just abstract away those webpages in order for others to consume those classes as they need:
*Curriculum class is a representation of the curriculum_visualization_page. This class should be instantiated with a short_it as an argument. Its instance will try to solve the required captchas and get the correct page at the end. If you don't need the xml and the data inside this page is enough, you could subclass this page and write methods for retireving data from the class attributes(source or soup) whatever you are more confortable with.
*Xml class is a representation of the xml_download_page/process. This class should be instantiated with a long_id and an output_directory for the downloaded files. Any instance of this class will then try to download the required captchas and download the long_id related xml.zip file.

## Requirements
python 3

Python libraries necessary:
* requests
* BeautifulSoup
* Pillow

## Installation
```
pip install requirements.txt
```

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
