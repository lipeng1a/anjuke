import requests,re
import urllib.request
from bs4 import BeautifulSoup
from lxml import etree
import pymysql
import pip
import time
from urllib import request
import random,ssl
print('连接到mysql服务器...')
db = pymysql.connect(host='localhost',
                         port=3306,
                         user='root',
                         passwd='7891230a',  #写上自己的数据库密码
                         db='test',      #所在的数据库
                         charset='utf8mb4') #可以插入4字节的非字符串类型*****
print('连接上了!')
cursor = db.cursor()
cursor.execute("DROP TABLE IF EXISTS ajk0505") #表名使用 来源-分类-日期的形式
print('删除已经存在的表')

sql = '''create table ajk0505(  
                                housepage varchar(5) default null ,
                                housenum  varchar(10) default null ,
                                region  varchar(20) default null , 
                                Hyperlink varchar(500) default null,
                                housid    varchar(30) default null ,
                                title varchar(800) default null,
                                houseencode varchar(50) default null,
                                community  varchar(100) default null,
                                Apartment  varchar(255) default null, 
                                unitprice varchar(100) default null,
                                area varchar(30) default null, 
                                paymentsfirst varchar(20) default null,
                                madeyear  varchar(10) default null,
                                tpyehous varchar(20) default null,
                                floor varchar(30) default null,
                                Renovation varchar(30) default null,
                                uesyear varchar(10) default null,
                                usedyear varchar(10) default null,
                                note varchar(1000) default null
                                )'''
cursor.execute(sql)
# 网页的请求头
header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
}
housepage = 1
housenum = 0

def get_page(url):  #在调用函数时，传入一个区的主页连接
    global housepage
    try:
        response = requests.get(url, headers=header)
    except:
        print("Connection refused by the server..")
        print("Let me sleep for 20 seconds")
        print("ZZzzzz...")
        time.sleep(20)
        response = requests.get(url, headers=header)
    #通过BeautifulSoup进行解析出每个房源详细列表并进行打印
    soup_idex = BeautifulSoup(response.text, 'html.parser')
    result_li = soup_idex.find_all('li', {'class': 'list-item'})
    # 进行循环遍历其中的房源详细列表
    for i in result_li:
        page_url = str(i)
        soup = BeautifulSoup(page_url, 'html.parser')
        # 由于通过class解析的为一个列表，所以只需要第一个参数
        result_href = soup.find_all('a', {'class': 'houseListTitle'})[0]
        # 获取到具体房源的连接后，调用详细信息页面的函数
        urlfun = result_href.attrs['href']
        urlneed = urlfun.split('?from')[0]
        get_page_detail(urlneed)   # 本页完成后指向下一页
    result_next_page = soup_idex.find_all('a', {'class': 'aNxt'})
    if len(result_next_page) != 0:   #!=连续递归
        # 函数进行递归
        get_page(result_next_page[0].attrs['href'])
        housepage +=1
        #pass
    else:
        print('没有下一页了')

def my_Beautifulsoup(response):
    return BeautifulSoup(str(response), 'html.parser')
# 详细页面的爬取
def get_page_detail(url):
    global housenum
    try:
        response = requests.get(url, headers=header)
    except:
        print("Connection refused by the server..")
        print("Let me sleep for 20 seconds")
        print("ZZzzzz...")
        time.sleep(20)
        response = requests.get(url, headers=header)
    # time.sleep(random.randint(1,2))
    if response.status_code == 200: #请求成功
        soup = BeautifulSoup(response.text, 'html.parser')
        title0 = soup.find_all('h3', {'class': 'long-title'})
        if not title0: #title0为空，需要手势验证，打开浏览器验证就行
            verify=input("先打开浏览器进行手势验证，然后随便输入都可以使程序继续进行：")
            response = requests.get(url, headers=header)
            soup = BeautifulSoup(response.text, 'html.parser')
            title0 = soup.find_all('h3', {'class': 'long-title'})
        housenum += 1
        # 地区、链接、id、标题等基本信息
        region_div = soup.find_all('div', {'class': 'p_1180 p_crumbs'})
        soup_1 = my_Beautifulsoup(region_div)
        #region = soup_1.find_all('a')[2].get_text()                           #获取地区--------------
        Hyperlink = url                                                        #房源链接-------------
        # print(Hyperlink)
        housid = url[38:]#房源id---------------
        title = title0[0].get_text()
        title =  title.replace('\n','')#房源title------------
        #房源基本信息
        #housecode = soup.find_all('span', {'id': 'houseCode'})[0].get_text()
        #housecode = re.findall(r"\d+\.?\d*", housecode)
        houseencode = soup.find_all('span', {'class': 'house-encode'})[0].get_text()      #房屋编码、发布时间---------
        houseencode = houseencode.split('： ')[1]
        houseencode = houseencode.split('                        ，')[0]

        community = soup.find_all('a', {'_soj': 'propview'})[0].get_text()                 #所属小区-------------------
        Apartment = soup.find_all('div', {'class': 'houseInfo-content'})[1].get_text()
        Apartment = Apartment.replace("\t", "")
        Apartment = Apartment.replace("\n", "")  #户型---------------------
        unitprice = soup.find_all('div', {'class': 'houseInfo-content'})[2].get_text()   #单价--------------------
        area = soup.find_all('div', {'class': 'houseInfo-content'})[4].get_text()        #面积-------------------
        paymentsfirst = soup.find_all('div', {'class': 'houseInfo-content'})[5].get_text()
        paymentsfirst = paymentsfirst.strip()                                                 #参考首付------------
        madeyear = soup.find_all('div', {'class': 'houseInfo-content'})[6].get_text()
        madeyear = madeyear.strip()                                                            #建造年代-----------
        tpyehous = soup.find_all('div', {'class': 'houseInfo-content'})[9].get_text()   #房屋类型-------
        floor =  soup.find_all('div', {'class': 'houseInfo-content'})[10].get_text()  #所在楼层---------
        Renovation =  soup.find_all('div', {'class': 'houseInfo-content'})[11].get_text()   #装修---------
        uesyear = soup.find_all('div', {'class': 'houseInfo-content'})[12].get_text()  # 装修---------
        usedyear = soup.find_all('div', {'class': 'houseInfo-content'})[14].get_text()  # 装修---------
        housinfo_div = soup.find_all('div', {'class': 'houseInfo-item'})
        note_span = my_Beautifulsoup(housinfo_div)
        #print(note_span)
        note = note_span.find_all('span')[1].get_text()                                          #房屋说明-----
        region_div_2 = soup.find_all('div', {'class': 'houseInfo-content'})[3]
        region_div_a = my_Beautifulsoup(region_div_2)
        region = region_div_a.find_all('a')[0].get_text()                                         # 地区--------------------
        print(region, housid, title, houseencode,note)
        #print(region, Hyperlink, housid, title, houseencode, community, Apartment, unitprice, area, paymentsfirst,madeyear,tpyehous,floor,Renovation,uesyear,usedyear)
        # -------------------------------------------------------------做插入数据库的操作-----------------------------------------------------------------
        insert_sql = "insert into ajk0505(housepage,housenum,region, Hyperlink, housid, title, houseencode, community, Apartment, unitprice, area, paymentsfirst,madeyear,tpyehous,floor,Renovation,uesyear,usedyear,note) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        insert_data = [housepage,housenum,region, Hyperlink, housid, title, houseencode, community, Apartment, unitprice, area, paymentsfirst,madeyear,tpyehous,floor,Renovation,uesyear,usedyear,note]  # 转换后字符串的插入数据
        cursor.execute(insert_sql, insert_data)
        # print('******完成此条插入!')
        db.commit()

if __name__ == '__main__':
    # url链接
    url = 'https://wuhan.anjuke.com/sale/hongshana/'  #集美、海沧、翔安 、湖里、同安、      已抓
   # 页面爬取函数调用
    get_page(url)