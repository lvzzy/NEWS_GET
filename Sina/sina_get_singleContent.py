#获取单条新闻的内容
import requests
from bs4 import BeautifulSoup
       
url = 'https://mil.news.sina.com.cn/2019-12-09/doc-iihnzahi6355412.shtml'
res = requests.get(url)
#print(res.encoding)
res.encoding = 'utf-8'
soup = BeautifulSoup(res.text, 'html.parser')
title = soup.select(".main-title")[0].text
print(title)
article_content = ""
article = soup.select('.article p')[:-1]#末端的消息来源不需要
for p in article:
    article_content = article_content + p.text.strip()
print(article_content)
