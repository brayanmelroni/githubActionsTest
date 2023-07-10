from bs4 import BeautifulSoup
import requests
import lxml
# Need external parsers

website = "https://www.sainsburys.co.uk"
result = requests.get(website)
content = result.text

soup = BeautifulSoup(content,'lxml')
print(soup.prettify())
