'''
1 获取"中新网"的滚动链接
2 解析详情页信息
3 存储入数据库
'''
import time
import sys
import os
import pymysql
from pymysql import Error
import requests
from multiprocessing import Pool
from bs4 import BeautifulSoup

from pandas.core.frame import DataFrame

#database connection
def con_db():
    try:
        global db
        db = pymysql.connect('localhost','root','123456','newsDB',charset='utf8')
    except pymysql.Error as e:
        print("Error: {}".format(e))
    cur = db.cursor()
    print('connection success')
    return cur

#get url list
def get_URL(url):
    res = requests.get(url,headers = headers)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    li_tag = soup.find('div','content_list').find_all('a')
    link_list = []
    for link in li_tag:
        url = 'http://www.chinanews.com'+str(link.get('href'))
        link_list.append(url)  
    return link_list

def parse(url):
    res = requests.get(url,headers = headers)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    news_title = soup.find('h1').text.strip()
    news_contents = ''
    contents = soup.find('div', 'left_zw').find_all('p')[2:-2]
    for content in contents:
        news_contents = news_contents + content.text.strip()
    try:
        insert_news(news_title,news_contents)
        return "success"
    except:
        return "sorry"

def insert_news(news_title,news_contents):
    category = '娱乐' #更改类别
    sqli = '''
        insert into 娱乐新闻(category,newsTitle,newsContent)
        values("%s","%s","%s")
    '''%(pymysql.escape_string(category),pymysql.escape_string(news_title),pymysql.escape_string(news_contents))
    cur.execute(sqli)
    time.sleep(1)


def main():
    global start
    start = time.time()
    global cur
    cur = con_db()
    init_url = 'http://www.chinanews.com/entertainment.shtml'#娱乐
    #init_url = 'http://www.chinanews.com/mil/news.shtml'#军事
    global headers
    headers = {'User-Agent':
                    'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/55.0.2883.87 Safari/537.36'}

    link_list = get_URL(init_url)

    pool = Pool(8) #create class of Processing Pool
    res_list = []
    for url in link_list:
        res = pool.apply_async(func=parse, args=(url,))
        res_list.append(res)

    record_list = []
    count = 0
    for res in res_list:
        count = count + 1
        try:
            result = res.get() #执行
            print('第'+ str(count) + '条新闻写入成功')
        except:
            print('第'+ str(count) + '条新闻抓取失败,正在尝试下一条')
            continue
        record_list.append(result)
 
    pool.close()
    pool.join() #Wait for all programs stopping and close pools

    global end
    end = time.time()

    cur.close()
    db.commit()# Commit all data to MySQL
    db.close()

if __name__ == "__main__":
    sys.setrecursionlimit(100000)  #设置默认递归深度
    main()
    print("共计用时:" + str(round((end-start)/60, 2)) + '分钟')
    