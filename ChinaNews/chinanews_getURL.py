'''
1 获取2019年4月之前的新闻链接
2 存入csv
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

#获取滚动页面的url
def get_url(date):
    url = 'http://www.chinanews.com/scroll-news/' + date +'/news.shtml'
    res = requests.get(url)
    res.encoding='GBK'  # html: ISO-8859-1 (2012)
    soup = BeautifulSoup(res.text, 'html.parser')

    li_tag = soup.find('div','content_list').find_all('li')
    category_list = []
    title_list = []
    url_list = []
    for li in li_tag:
        try:
            info = li.find_all('a')
            category = info[0].text
            if category in ['军事','娱乐','台湾','汽车','教育','健康']:
                category_list.append(category)
                news_title = info[1].text
                title_list.append(news_title)
                news_url = 'http://www.chinanews.com'+str(info[1].get('href'))
                url_list.append(news_url)
                print("have done!"+ news_title+":"+news_url)
        except:
            continue
    print()
    c = {'类别':category_list,
        '标题':title_list,
        'url':url_list
    }
    data=DataFrame(c)
    root = ".//newsCollection//"
    path = root + "chinanews00.csv"
    try:
        if not os.path.exists(root):
                os.mkdir(root)
                print('mkdir success')
        data.to_csv(path, mode='a')
    except IOError:
        print('sorry, write failed')
    else:
        print("---chinanews01.csv have been added---")

def get_date():
    dates = []
    year = 2012
    for month in range(6,13):
        if month in [1,3,5,7,8,10,12]:
            for day in range(1,32):
                a = str(year)+'/'+str(month).zfill(2)+str(day).zfill(2)
                dates.append(a)
        elif month in [4,6,9,11]:
            for day in range(1,31):
                a = str(year)+'/'+str(month).zfill(2)+str(day).zfill(2)
                dates.append(a)
    return dates

def main():
    pool = Pool(8) #create class of Processing Pool
    dates = get_date()
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