'''
获取网易新闻
1 获取排行榜上的新闻链接(list)
3 获取新闻 标题,正文内容 (类别之后存储时添加)
4 将新闻保存为dataframe格式,并输出为csv文件
'''
import requests
from bs4 import BeautifulSoup
import os
import csv
from pandas.core.frame import DataFrame

#original html
url = 'http://news.163.com/special/0001386F/rank_ent.html'
headers = {'User-Agent':
               'Mozilla/5.0 (Windows NT 10.0; WOW64) '
               'AppleWebKit/537.36 (KHTML, like Gecko) '
               'Chrome/55.0.2883.87 Safari/537.36'}
            
res = requests.get(url, headers = headers) 
res.content.decode('gb18030','ignore') #原网页gbk
#res.encoding = 'utf-8'
soup = BeautifulSoup(res.text, 'html.parser')
#print(soup.prettify())
titles = soup.find('div', 'area-half left').find('div', 'tabContents active').find_all('a') #list

newsTitle = []
newsContent = []
for title in titles:
    #get urls from html
    news_url = (str(title.get('href')))
    #read each url 
    news_response = requests.get(news_url, headers=headers)
    news_html = news_response.text
    news_soup = BeautifulSoup(news_html, 'html.parser')
    #analyze html to find news' title and news' content
    if news_soup.find('div', 'post_text') is None:  #if html loose, jump out circulation
        continue
    news_title = news_soup.find('h1')
    contents = news_soup.find('div', 'post_text').find_all('p')[:-2]
    news_contents = ""
    for content in contents:
        if len(content.text)<=0 or ("video" in content.text):
            continue
        else:
           news_contents = news_contents + content.text.strip()
    #join to list to becoming dataframe
    newsTitle.append(news_title.text)
    newsContent.append(news_contents)

#shift to dataframe and print to csv_file
c =  {
    "category":"娱乐",
    "newsTitle":newsTitle,
    "newsContent":newsContent
}
news_data = DataFrame(c)

root = ".//newsCollection//"
path = root + "wangyi03.csv"
try:
    if not os.path.exists(root):
            os.mkdir(root)
            print('mkdir success')
    news_data.to_csv(path)
except IOError:
    print('sorry, write failed')
else:
    print('write in success')
