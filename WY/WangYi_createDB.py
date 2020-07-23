#将读取的数据写入数据库
#https://www.runoob.com/python3/python-mysql-connector.html
import mysql.connector

#create database 
news_db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "123456"
)
mycur = news_db.cursor()
#mycur.execute("CREATE DATABASE newsDB")
mycur.execute("SHOW DATABASES")
for x in mycur:
    print(x)