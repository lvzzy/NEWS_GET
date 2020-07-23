'''
1 读取csv文件,获取链接
2 解析链接,获取详情页信息
3 存储为新表
'''
import time
import sys
import os
import requests
from multiprocessing import Pool
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame

headers = {'User-Agent':
             'Mozilla/5.0 (Windows NT 10.0; WOW64) '
             'AppleWebKit/537.36 (KHTML, like Gecko) '
             'Chrome/55.0.2883.87 Safari/537.36'}
#get url from csv file
def get_url():
    data = pd.read_csv('.//newsCollection//军事.csv')
    url_list = data['url']
    url_list = url_list.tolist()
    return url_list

def parse(news_url):
    #read each url 
    news_response = requests.get(news_url, headers=headers)
    news_response.encoding = 'utf-8'
    news_soup = BeautifulSoup(news_response.text, 'html.parser')
    category_list = []
    title_list = []
    url_list = []
    content_list = []
    #analyze html to find news' title and news' content
    category_list.append('军事')#每次添加的类别待修改
    news_title = news_soup.select(".main-title")[0].text
    title_list.append(news_title)
    news_contents = ""
    contents = news_soup.select('.article p')[:-1]
    for content in contents:
        news_contents = news_contents + content.text.strip() 
    url_list.append(news_url)
    content_list.append(news_contents)

    #save in csv
    c = {'category':category_list,
        'title':title_list,
        'url':url_list,
        'content':content_list
    }
    data=DataFrame(c)
    root = ".//newsCollection//"
    path = root + "sinanews军事.csv"#此处许修改!!!
    try:
        if not os.path.exists(root):
                os.mkdir(root)
                print('mkdir success')
        data.to_csv(path, mode='a',header=None ,index=False, encoding="utf-8-sig")
    except IOError:
        print('sorry, write failed')
    else:
        print("---sinanews军事.csv have been added---")

def main():
    url_list = get_url()
    pool = Pool(8) #create class of Processing Pool
    res_list = []
    for url in url_list:
        res = pool.apply_async(func=parse, args=(url,))
        res_list.append(res)

    record_list = []
    count = 0
    for res in res_list:
        count = count + 1
        try:
            result = res.get() #执行
            print('第'+ str(count) + '页链接获取成功')
        except:
            print('第'+ str(count) + '页链接获取失败,正在尝试下一页')
            continue
        record_list.append(result)
 
    pool.close()
    pool.join() #Wait for all programs stopping and close pools

if __name__ == "__main__":
    main()