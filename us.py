from lxml import etree
from requests import session

URL = "https://www.google.com/search?q=2020+presidential+election"

session = session()
page = session.get(URL)
print(page.status_code)
html = etree.HTML(page.text, etree.HTMLParser())
print(2)