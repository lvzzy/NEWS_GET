#多进程读取
'''
1 获取网易排行榜的title
2 解析title,进入链接,获取新闻内容(多进程)
3 存储入数据库
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

#analyze initpage to get title list
def Initpage(url, headers):
    res = requests.get(url, headers = headers) 
    res.content.decode('gb18030','ignore') #原网页gbk
    soup = BeautifulSoup(res.text, 'html.parser')
    #print(soup.prettify())
    titles = soup.find('div', 'area-half left').find('div', 'tabContents active').find_all('a') #list
    return titles

#analyze each elements to get urls,newsTitle,newsContent
def parse(title):
    #get urls from html
    news_url = (str(title.get('href')))
    #read each url 
    news_response = requests.get(news_url, headers=headers)
    news_html = news_response.text
    news_soup = BeautifulSoup(news_html, 'html.parser')
    #analyze html to find news' title and news' content
    if news_soup.find('div', 'post_text') is None:  #if html loose, jump out circulation
        return 
    news_title = news_soup.find('h1').text
    contents = news_soup.find('div', 'post_text').find_all('p')[:-2]
    news_contents = ""
    for content in contents:
        if len(content.text)<=0 or ("video" in content.text) or ("img" in content.text):
            continue
        else:
            news_contents = news_contents + content.text.strip()
    try:
        insert_news(news_title,news_contents)
        return "success"
    except:
        return "sorry"
        
        
def insert_news(news_title,news_contents):
    category = '教育' #更改类别
    sqli = '''
        insert into 教育新闻(category,newsTitle,newsContent)
        values("%s","%s","%s")
    '''%(pymysql.escape_string(category),pymysql.escape_string(news_title),pymysql.escape_string(news_contents))
    cur.execute(sqli)
    time.sleep(1)

def main():
    global start
    start = time.time()
    global cur
    cur = con_db()
    #init_url = 'http://news.163.com/special/0001386F/rank_ent.html'#娱乐
    #init_url = 'http://news.163.com/special/0001386F/rank_sports.html'#体育
    #init_url ='http://money.163.com/special/002526BH/rank.html'#财经
    #init_url ='http://news.163.com/special/0001386F/rank_tech.html'#科技
    #init_url ='http://news.163.com/special/0001386F/rank_auto.html'#汽车
    #init_url ='http://news.163.com/special/0001386F/rank_house.html'#房产
    #init_url ='http://news.163.com/special/0001386F/game_rank.html'#游戏
    #init_url ='http://news.163.com/special/0001386F/rank_travel.html'#旅游
    init_url ='http://news.163.com/special/0001386F/rank_edu.html'#教育
    global headers
    headers = {'User-Agent':
                    'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/55.0.2883.87 Safari/537.36'}
    titles = Initpage(init_url,headers)
   
    #part of multiprocessing
    pool = Pool(8) #create class of Processing Pool

    res_list = []
    for title in titles:   #将任务设置进入进程池
        res = pool.apply_async(func=parse, args=(title,))
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



    
