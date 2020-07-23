'''
获取"中国新闻网"url详情页的信息
'''

import requests
from bs4 import BeautifulSoup
url = 'http://www.chinanews.com/auto/2019/01-30/8743035.shtml'
res = requests.get(url)
res.encoding='GBK'  # html: ISO-8859-1 (2012)
# res.encoding = 'utf-8' # (2019)
soup = BeautifulSoup(res.text, 'html.parser')

title = soup.find('h1')
print(title.text.strip())
news_contents = ''
contents = soup.find('div', 'left_zw').find_all('p')
for content in contents:
    if 'function' in content.text:
        continue
    news_contents = news_contents + content.text.strip()
print(news_contents)
