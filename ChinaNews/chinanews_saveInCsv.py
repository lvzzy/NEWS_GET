'''
1 "中新网" 滚动页面获取链接
2 解析链接,获取新闻内容
3 将结果写入csv文件
'''
import time
import sys
import os
# import pymysql
# from pymysql import Error
import requests
from multiprocessing import Pool
from bs4 import BeautifulSoup
from pandas.core.frame import DataFrame

headers = {'User-Agent':
                    'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/55.0.2883.87 Safari/537.36'}
#获取滚动页面的url
def get_url(date):
    url = 'http://www.chinanews.com/scroll-news/' + date +'/news.shtml'
    res = requests.get(url,headers=headers)
    res.encoding='GBK'  # html: ISO-8859-1 (2012)
    #res.encoding = 'utf-8' # (2019)
    soup = BeautifulSoup(res.text, 'html.parser')

    li_tag = soup.find('div','content_list').find_all('li')
    category_list = []
    title_list = []
    url_list = []
    content_list = []
    for li in li_tag:
        try:
            info = li.find_all('a')
            category = info[0].text
            if category in ['台湾','汽车','教育','健康','军事']:
                category_list.append(category)
                news_title = info[1].text
                title_list.append(news_title)
                news_url = str(info[1].get('href'))
                if 'http' not in news_url:
                    news_url = 'http://www.chinanews.com' + news_url
                url_list.append(news_url)
                try:
                    content = get_contents(news_url)
                except:
                    content = " "
                content_list.append(content)
                print("have done!"+ news_title+":"+news_url)
        except:
            continue
    c = {'category':category_list,
        'title':title_list,
        'url':url_list,
        'content':content_list
    }
    data=DataFrame(c)
    root = ".//newsCollection//"
    path = root + "chinanews2013_1.csv"#此处许修改
    try:
        if not os.path.exists(root):
                os.mkdir(root)
                print('mkdir success')
        data.to_csv(path, mode='a', header=None, index=False, encoding="utf-8-sig")
    except IOError:
        print('sorry, write failed')
    else:
        print("---chinanews2013_1.csv have been added---")

def get_contents(url):
    res = requests.get(url,headers=headers)
    res.encoding='GBK'  # html: ISO-8859-1 (2012)
    #res.encoding = 'utf-8' # (2019)
    soup = BeautifulSoup(res.text, 'html.parser')

    news_contents = ''
    contents = soup.find('div', 'left_zw').find_all('p')[1:-1]
    for content in contents:
        if 'function' in content.text:
            continue
        news_contents = news_contents + content.text.strip()
    return news_contents

def get_date():
    dates = []
    year = 2012
    for month in range(5,13):
        if month in [1,3,5,7,8,10,12]:
            for day in range(1,32):
                a = str(year)+'/'+str(month).zfill(2)+str(day).zfill(2)
                dates.append(a)
        elif month in [4,6,9,11]:
            for day in range(1,31):
                a = str(year)+'/'+str(month).zfill(2)+str(day).zfill(2)
                dates.append(a)
        else:
            for day in range(1,29):
                a = str(year)+'/'+str(month).zfill(2)+str(day).zfill(2)
                dates.append(a)
    return dates

def main():
    pool = Pool(8) #create class of Processing Pool
    #dates = get_date()
    dates = ['2012/1229','2012/1230','2012/1231']
    res_list = []
    for date in dates:
        res = pool.apply_async(func=get_url, args=(date,))
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
