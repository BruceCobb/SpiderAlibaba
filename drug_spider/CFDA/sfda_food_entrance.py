# -*- coding:utf-8 -*-

import MySQLdb
import time
import random
import re
from selenium import webdriver
from bs4 import BeautifulSoup
import sys
import requests
import logging
import traceback
reload(sys)
sys.setdefaultencoding('utf8')


class sfda_drug():
    def __init__(self):
        # db_data
        self.host = "127.0.0.1"
        self.db = "for_es"
        self.user = "root"
        self.passwd = "root"
        self.port = 3306
        self.conn = None
        # url参数和遍历参数
        self.cur_page = 1  # 当前药品页数
        self.cur_item = 1  # 当前药品个数
        self.max_page = 52  # 药品的总页数
        self.max_item = 773  # 药品的总个数
        self.table_id = 31  # 进口食品
        self.base_url = "http://app1.sfda.gov.cn/datasearch/face3/search.jsp?tableId=%d&bcId=124356651564146415214424405468&curstart=%d"
        self.drug_url = "http://mobile.cfda.gov.cn/datasearch/QueryRecord?tableId=%d&searchF=ID&searchK=%d"
        self.proxy_url = "http://proxy.httpdaili.com/api.asp?ddbh=126656543710234527&noinfo=true&sl=3&text=1"
        # 数据库参数
        self.status_table = "sfda_food_entrance_id_status"
        self.drug_table = "sfda_food_entrance"
        self.headers = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
        self.proxy = False  # 关闭代理
        logging.basicConfig(filename='sfda_food_entrance.log') # 日志输出文件
        

    def req_sleep(self, *kw):
        """执行不同的延时计划"""
        if kw[0] == "random":
            time.sleep(random.randint(kw[1], kw[2]))
        if kw[0] == "normal":
            time.sleep(0)
        if kw[0] == "except":
            time.sleep(2)

    def dynamic_proxy(self):
        """获取代理IP地址"""
        response = requests.get(url=self.proxy_url, timeout=10)
        proxy_list = response.text.encode("utf-8").split("\r\n")
        return proxy_list

    def true_url(self, *kw):
        """根据参数组合不同的url"""
        if kw[0] == "id":
            return self.base_url % (kw[1], kw[2])
        if kw[0] == "search_key":
            return self.drug_url % (kw[1], kw[2])

    def db_conn(self):
        self.conn = MySQLdb.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            passwd=self.passwd,
            db=self.db,
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

    def get_drug_id(self):
        while self.cur_page <= self.max_page:
            print "--正在获取 -%d- 页的数据--" % self.cur_page
            try:
                # ip = self.dynamic_proxy()[random.randint(0, 2)]
                # chrome proxy
                # options = webdriver.ChromeOptions()
                # options.add_argument('--proxy-server=http://' + ip)
                # driver = webdriver.Chrome(chrome_options=options)
                driver = webdriver.Chrome()
                # driver = webdriver.PhantomJS(service_args=['--proxy=' + ip])
                driver.set_page_load_timeout(20)
                driver.get(self.true_url("id", self.table_id, self.cur_page))
                html = driver.page_source
                # 解析数据存入mysql
                self.parse_html(html)
                driver.close()
                self.req_sleep("normal")
                self.cur_page += 1
            except Exception as e:
                print "--异常信息为:\n%s" % e
                self.req_sleep("except")
                driver.quit()

    def parse_html(self, html):
        soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
        a_list = soup.find_all('a')
        if a_list:
            sql_list = list()
            for a in a_list:
                a = a.attrs['href']
                ID = re.findall(r"&Id=(\d+)", a)
                sql = "INSERT INTO {} VALUES ({}, {}, {});".format(self.status_table, 0, int(ID[0]), 0)
                sql_list.append(sql)
            self.dbExecu_list(sql_list)

    def get_drug_data(self):
        sql = "SELECT distinct drug_id from {} where status = 0;".format(self.status_table)
        cur = self.dbExecu(sql)
        fail_id = 0
        while True:
            if fail_id == 0:
                drug_id = int(cur.fetchone()[0])
                if not drug_id:
                    cur.close()
                    return
            else:
                drug_id = fail_id
            print "--正在获取ID为 -%d- 数据--" % drug_id
            try:
                response = requests.get(url=self.true_url("search_key", self.table_id, drug_id),
                                        timeout=10)
                drugs_data = response.json()
                drug_list = self.parse_info(drugs_data)
                self.update_drug_data(drug_list, drug_id)
                fail_id = 0
                self.req_sleep("normal")
            except Exception as e:
                print "--异常信息为:--\n%s" % e
                self.req_sleep("except")
                fail_id = drug_id

    def parse_info(self, drug_data):
        drug_dict = dict()
        for drug in drug_data:
            name = drug["NAME"]
            content = drug["CONTENT"]
            drug_dict[name] = content
        return drug_dict

    def update_drug_data(self, drug, drug_id):
        sql_drug = """insert into {} values (0 , {}, "{}","{}","{}","{}","{}","{}",
                                                     "{}","{}","{}","{}","{}","{}",
                                                     "{}","{}","{}","{}","{}")""".format(
            self.drug_table, drug_id, 
            MySQLdb.escape_string(drug[u"产品英文名称"]), 
            MySQLdb.escape_string(drug[u"批准日期"]), 
            MySQLdb.escape_string(drug[u"申请人中文名称"]), 
            MySQLdb.escape_string(drug[u"产品编号"]), 
            MySQLdb.escape_string(drug[u"批准文号"]), 
            MySQLdb.escape_string(drug[u"产品中文名称"]),
            MySQLdb.escape_string(drug[u"申请人英文名称"]), 
            MySQLdb.escape_string(drug[u"申请人地址"]), 
            MySQLdb.escape_string(drug[u"生产企业中文名称"]), 
            MySQLdb.escape_string(drug[u"生产国（地区）"]), 
            MySQLdb.escape_string(drug[u"食用方法及食用量"]),
            MySQLdb.escape_string(drug[u"备案内容"]),
            MySQLdb.escape_string(drug[u"受让方英文名称"]),
            MySQLdb.escape_string(drug[u"有效期至"]),
            MySQLdb.escape_string(drug[u"注销日期"]),
            MySQLdb.escape_string(drug[u"产品技术要求"]),
            MySQLdb.escape_string(drug[u"注"]),
        )

        sql_status = "update {} set status = 1 where drug_id = {}".format(self.status_table, drug_id)
        self.dbExecu_list([sql_drug, sql_status])


    def run(self):
        self.db_conn()

        # 第一步：获取药品的Id
        # self.get_drug_id()
        # 第二步：根据药品Id获取药品信息
        self.get_drug_data()

        self.db_close()


if __name__ == '__main__':
    sfda = sfda_drug()
    sfda.run()



