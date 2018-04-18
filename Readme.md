# CNPQ
Captcha Negated by Python reQuests - For the CNPq lattes database.

The Lattes curriculum database was supposed to be of public access according to federal laws, however its managers are denying public/free access by placing captchas to:
* Simply vizualize the curriculum
* To download the xml representation of the curriculum
Bear in mind that in order to download the xml one needs to vizualize the curriculum first. This implies that in order to download a single curriculum, one must solve 2 captchas. This is unaceptable.

Restrictions:
1. In order to get the xmls, we need long_ids: a [0-9]{16} length string. This is only shown inside the the page where we can vizualize the curriculum page.
2. In order to go vizualize a curriculum page, we need a short_id: a [A-Z0-9]{10} length string. This can be retrieved inside its search system.
So, for example: This short_id: K4260007T6 is related to this long_id: 6380212729787758
The problem was broken into 3 parts, which are necessary for getting the final result: a xml file.

Architecture:
As opposite to building a script, I'll just abstract away those webpages in order for others to consume those classes as they need:
*CurriculumPage is a class where when initialized with a short_id, will navigate to the curriculum page, breaking the capthca in the process. In the current state the only attributes that matter are the source_code and the long_id. However it can be subclassed in order to get other attributes from its source code the same way we did with long_id. In other words, if all one need can be found in the curriculum vizualization page, this is all one needs.
*CurriculumXml is a class where when initialized with a long_id and a download directory, will navigate to the xml page breaking the capthca in the process nad finally downloading the corresponding xml.zip file.

## Requirements
python 3

Python libraries necessary:
* requests
* BeautifulSoup
* lxml
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
