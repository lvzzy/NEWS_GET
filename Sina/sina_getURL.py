'''
获取 新浪滚动新闻 的链接
存储为csv文件
'''
import time
import sys
import os
import requests
from multiprocessing import Pool
from bs4 import BeautifulSoup
from pandas.core.frame import DataFrame

def get_URL(i):
    #init_url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2513&k=&num=50&page={}'#娱乐
    #init_url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2511&k=&num=50&page={}'#国际
    #init_url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2512&k=&num=50&page={}'#体育
    #init_url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2514&k=&num=50&page={}'#军事
    init_url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2515&k=&num=50&page={}'#科技
    #init_url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2516&k=&num=50&page={}'#财经
    page = requests.get(url=init_url.format(i), headers=headers).json()
    links = []
    for j in range(50):
        urls = page['result']['data'][j]['url']
        links.append(urls)
    return links

def main():
    global headers
    headers = {'User-Agent':
                        'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/55.0.2883.87 Safari/537.36'}
    pagenum = 50 #choose pagenum u want to scrapy
    link_list = []
    for i in range(1,pagenum):
        try:          
            links = get_URL(i)
            link_list = link_list + links
        except:
            print("第"+str(i)+"页链接获取失败")
        else:
            print("第"+str(i)+"页链接已经全部获取")

    c = {'url':link_list}
    data = DataFrame(c)
    
    root = ".//newsCollection//"
    path = root + "科技.csv"
    try:
        if not os.path.exists(root):
            os.mkdir(root)
            print('mkdir success')
        data.to_csv(path)
    except IOError:
        print('sorry, write failed')
    else:
        print("---科技.csv have created---")

if __name__ == "__main__":
    sys.setrecursionlimit(100000)  #设置默认递归深度
    main()
    #print("共计用时:" + str(round((end-start)/60, 2)) + '分钟')