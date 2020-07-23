'''
1 获取 新浪新闻 某网页上的全部链接
2 访问链接 获取新闻内容
3 存储到数据库
'''
import time
import sys
import pymysql
from pymysql import Error
import requests
from multiprocessing import Pool
from bs4 import BeautifulSoup

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

#analyze initpage to get link list
def Initpage(url, headers):
    res = requests.get(url, headers = headers) 
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    li_tag = soup.select('li')[12:]
    return li_tag

#analyze each elements to get urls,newsTitle,newsContent
def parse(li):
    #get urls from html
    news_url = li.select('a')[0]['href']
    #read each url 
    news_response = requests.get(news_url, headers=headers)
    news_response.encoding = 'utf-8'
    news_soup = BeautifulSoup(news_response.text, 'html.parser')
    #analyze html to find news' title and news' content
    news_title = news_soup.select(".main-title")[0].text

    news_contents = ""
    contents = news_soup.select('.article p')[:-1]
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

    #init_url = 'https://auto.sina.com.cn/'#汽车
    init_url = 'https://ent.sina.com.cn/' #娱乐
    #init_url = 'https://finance.sina.com.cn/'#财经
    #init_url = 'https://tech.sina.com.cn/' #科技
    #init_url = 'https://mil.news.sina.com.cn/'#军事
    
    #init_url = 'http://sports.sina.com.cn/'#体育
    #init_url = 'http://edu.sina.com.cn/'#教育
    #init_url = 'http://travel.sina.com.cn/'#旅游,失效
    #init_url = 'https://games.sina.com.cn' #游戏,完全失败
    global headers
    headers = {'User-Agent':
                    'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/55.0.2883.87 Safari/537.36'}
    li_tag = Initpage(init_url,headers)
   
    #part of multiprocessing
    pool = Pool(8) #create class of Processing Pool

    res_list = []
    for li in li_tag:   #将任务设置进入进程池
        res = pool.apply_async(func=parse, args=(li,))
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


