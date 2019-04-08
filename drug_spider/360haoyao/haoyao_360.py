# -*- coding:utf-8 -*-

import time
import re
import logging
import traceback
import random
import requests
from selenium import webdriver
from fake_useragent import UserAgent
from lxml import etree
import jieba
import os
import sys
import traceback
import MySQLdb
import threading
import json
reload(sys)
sys.setdefaultencoding('utf8')


class haoyao_360():

    def __init__(self):
        self.conn = None
        self.host_address = '/Users/bruce/MEGAsync/Work_Projects/spider/'
        self.base_url = "http://www.360haoyao.com/list/1019?&gotoPage="
        self.pic_base_url = "http://pic3.360img.cn/"
        self.host_postfix = '.html'
        self.host_base_data = {}
        self.host_username = "140.143.241.223"
        self.host_password = "Gaoji_001#"
        self.logger = logging.basicConfig(filename='haoyao_360.log')
        self.reg = {
                "url": "//p[@class='listName']/a/@href",
                "title": "//div[@class='dtlInfoMid']/h1/span/text()",
                "functional": "//div[@class='textureTit']/span/text()",
                "price": "//span[@class='good_price fl']/em/text()",
                "product_num":"//li[@class='item_number']/text()",

                "img_show_list" : "//ul[@id='thumblist']//a/@rel",
                "specification_list": "//table[@class='desTable']//text()",
                "img_content_list": "//div[@id='prodDetailCotentDiv']//img/@src",
                }
        # db_data
        self.host = "127.0.0.1"
        self.db = "gaoji_drug_data"
        self.user = "root"
        self.passwd = "root"
        self.port = 3306
        self.conn = None
        self.charset = 'utf8'

    def db_conn(self):
        self.conn = MySQLdb.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            passwd=self.passwd,
            db=self.db,
            charset=self.charset
        )

    def db_close(self):
        self.conn.close()

    def dbExecu_list(self, sql_list):
        for sql in sql_list:
            if sql == '' or sql == None:
                return False
            try:
                cur = self.conn.cursor()
                cur.execute(sql)
                self.conn.commit()
            except Exception as e:
                print "SQL:\n%s" % sql
                logging.error(traceback.format_exc())
                logging.error(sql)
                self.conn.rollback()

    def dbExecu(self, sql):
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            return cur
        except Exception as e:
            print "SQL:\n%s" % sql
            logging.error(traceback.format_exc())
            logging.error(sql)
            self.conn.rollback()

    def get_header(self):
        """获取不同的报文头"""
        browser = ['chrome','firefox','safari']
        headers = {"User-Agent": getattr(UserAgent(), str(random.choice(browser)))}
        return headers
        
    def get_sleep(self, *kw):
        """执行不同的延时计划"""
        if kw[0] == "random":
            time.sleep(random.randint(kw[1], kw[2]))
        elif kw[0] == "zero":
            time.sleep(0)
        elif kw[0] == "decimal":
            time.sleep(0.5)
        elif kw[0] == "normal":
            time.sleep(1)
        elif kw[0] == "except":
            time.sleep(2)
        elif kw[0] == "img":
            time.sleep(0.5)

    def get_url(self, url, *kw):
        """根据参数组合url"""
        for k in kw:
            url = url + str(k)
        return url

    def get_url_filt(self, url):
        """给url加上http前缀:"""
        pattern = re.compile(r'^http:*')
        res = pattern.match(url)
        if res is None:
            url = 'http:' + url
            return url
        else:
            return url

    """
    核心功能
    """

    def haoyao_engine(self, page, page_end):
        """爬虫引擎函数"""
        sign = 0
        urls = ""
        page = page
        while True:
            try:
                # 请求意外失败,5次之内重新获取
                if sign != 0 and sign >= 5:
                    page = page + 1
                    sign = 0
                    continue

                print "--正在获取第{}页的数据--".format(page)
                true_page_url = self.get_url(self.base_url, page)
                # 第1步:提取链接
                urls = self.get_haoyao_page(true_page_url)

            except Exception as e:
                sign = sign + 1
                continue

            # 第2步:提取数据
            self.get_haoyao_content(urls, page)

            # 第3步:持久化数据
            # self.write_document(haoyao_content)

            page = page + 1
            sign = 0
            # 指定终点页数
            if page == page_end:
                return

    def get_haoyao_page(self, url):
        """获取一页的文章链接列表"""
        response = requests.get(url, headers = self.get_header())
        urls = self.parse_haoyao_data(response.content)
        return urls

    def parse_haoyao_data(self, content):
        """返回每一页的链接集合"""
        html = etree.HTML(content)
        reg = self.reg["url"]
        haoyao_list = html.xpath(reg)
        if len(haoyao_list) == 0:
            return False
        return haoyao_list

    def get_haoyao_content(self, urls, page):
        """返回每一页的数据集合"""
        drug_page = 0
        sign = 0

        # 火狐静默设置
        fireFoxOptions = webdriver.FirefoxOptions()
        fireFoxOptions.set_headless()

        # chrome静默设置
        chromeOptions = webdriver.ChromeOptions()
        # chromeOptions.set_headless()

        driver = webdriver.Chrome(chrome_options=chromeOptions)

        driver.set_page_load_timeout(15)

        driver.implicitly_wait(20)

        while True:
            # 睡眠1秒
            time.sleep(2)
            # 循环结束的条件
            if drug_page >= len(urls):
                break

            haoyao_url = urls[drug_page]
            print "--正在获取第{}页的第{}个药品--".format(page, drug_page+1)
            try:

                # 请求意外失败,5次之内重新获取
                if sign!=0 and sign >= 5:
                    sign = 0
                    drug_page = drug_page + 1
                    continue

                # 请求地址
                driver.get(haoyao_url)
                driver.execute_script("window.scrollTo(0,10000)")
                # response = requests.get(haoyao_url, headers=self.get_header(), timeout=10)
                self.get_sleep("img")

                html = driver.page_source

                self.parse_content_data(haoyao_url, html)

            except Exception as e:
                self.get_sleep("except")
                # 数据获取异常
                # print e
                sign = sign + 1

            # 本药抓取结束
            sign = 0
            drug_page = drug_page + 1

        # 循环完后关闭
        driver.quit()

    def parse_content_data(self, haoyao_url, content):
        """解析文章的内容,写入文件"""
        html = etree.HTML(content)

        # 药品 简述
        title = html.xpath(self.reg["title"])[0]
        functional =  html.xpath(self.reg["functional"])[0]

        price = html.xpath(self.reg["price"])[0]
        product_num = html.xpath(self.reg["product_num"])[0]

        # 药品 图片
        img_show_list = html.xpath(self.reg["img_show_list"])

        # 药品 详情
        specification_list = html.xpath(self.reg["specification_list"])
        img_content_list = html.xpath(self.reg["img_content_list"])

        # print "-----测试数据-----"

        drug_data =  {
                "haoyao_url": haoyao_url,
                "title": title,
                "functional": functional,
                "price": price,
                "product_num": product_num,

                "img_show_list": img_show_list,

                "specification_list": specification_list,
                "img_content_list": img_content_list,
                }

        self.write_document(drug_data)

    def write_document(self, haoyao_content):
        """把数据写入文件"""

        # 解析图片数据
        full_img = json.dumps(haoyao_content["img_show_list"], ensure_ascii=False)

        # 解析内容数据
        specification_list = json.dumps(haoyao_content["specification_list"], ensure_ascii=False)

        img_content_list = json.dumps(haoyao_content["img_content_list"], ensure_ascii=False)

        # 持久化数据
        sql_drug = """insert into `360haoyao_drug` values (0 , "{}","{}","{}","{}","{}")""".format(
            MySQLdb.escape_string(haoyao_content["haoyao_url"]),
            MySQLdb.escape_string(haoyao_content["title"]),
            MySQLdb.escape_string(haoyao_content["functional"]),

            MySQLdb.escape_string(haoyao_content["price"]),
            MySQLdb.escape_string(haoyao_content["product_num"]),

            # MySQLdb.escape_string(full_img),

            # MySQLdb.escape_string(specification_list),
            # MySQLdb.escape_string(img_content_list),

            )
        self.dbExecu(sql_drug)


if __name__ == '__main__':
    haoyao = haoyao_360()
    haoyao.db_conn()
    threading.Thread(target=haoyao.haoyao_engine(50, 100)).start()
    haoyao.db_close()
