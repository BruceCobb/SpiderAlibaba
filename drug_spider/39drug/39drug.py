#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/25 下午4:33
# @Author  : Rill(wli)
# @Site    :
# @File    : spider_5.py
# @Software: PyCharm
import spider_request
import spider_parse
import re, json
import MySQLdb
from lxml import etree
import requests
import time
from multiprocessing import freeze_support, Pool, Lock
from HTMLParser import HTMLParser
from fake_useragent import UserAgent
import threading
import random
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

number = 0
cor = list()
# proxy_ = ""
#
#
# def get_proxy():
#     global proxy_
#     while True:
#         proxy_url = "http://proxy.httpdaili.com/apinew.asp?text=true&noinfo=true&sl=10&ddbh=145967976925544552"
#         res = requests.get(proxy_url)
#         data = res.content.split('\r\n')
#         ip_ = random.choice(data)
#         proxy_ = {"http": "%s" % ip_}


def run(id_, manbing_disease_url):
    global number, cor
    url = manbing_disease_url + "manual"
    k = 0
    while True:
        s = requests.session()
        s.keep_alive = False
        if k >= 3:
            break
        print id_, url
        try:
            res = spider_request.request_get_url(url)
        except Exception as e:
            print '页面请求报错%s' % e
            k += 1
            continue
        html = etree.HTML(res.text)
        data = html.xpath('//div[@class="tab_box"]')
        if len(data) == 0:
            print 'data 为空'
            k += 1
            continue
        # print HTMLParser().unescape(etree.tostring(data[0]))
        i = 1
        li_ = list()
        k = 1
        j = 1
        while True:
            dict_ = {}
            try:

                x_s = '//div[@class="tab_box"]//dl[{}]/dt'.format(i)
                title = spider_parse.contentsub(HTMLParser().unescape(etree.tostring(html.xpath(x_s)[0])))
                x_s_too = '//div[@class="tab_box"]//dl[{}]/dd'.format(i)
                content = spider_parse.contentsub(HTMLParser().unescape(etree.tostring(html.xpath(x_s_too)[0])))
                k += 1
            except IndexError as e:
                j += 1
                print(e)
                break
            dict_[title] = content
            li_.append(dict_)
            i += 1
        print('ok:{}'.format(k))
        print('error:{}'.format(j))
        info = json.dumps(li_, encoding='utf-8', ensure_ascii=False)
        print info
        db = MySQLdb.connect(host='localhost', user='root', passwd='root', db='gaoji_drug_data', port=3306, charset='utf8')
        cur = db.cursor()
        sql = "update gj_39_manbing_disease_info set indication_json='{}' where id = '{}' ".format(
            MySQLdb.escape_string(info),
            id_
        )
        # print sql
        cur.execute(sql)
        db.commit()
        db.close()
        break


if __name__ == "__main__":
    db = MySQLdb.connect(host='localhost', user='root', passwd='root', db='gaoji_drug_data', port=3306, charset='utf8')
    cur = db.cursor()
    freeze_support()
    pool = Pool(6)
    sql = "select id, manbing_disease_url from gj_39_manbing_disease_info where indication_json is NULL"
    cur.execute(sql)
    data = cur.fetchall()
    db.close()
    num = 1
    for id_, manbing_disease_url in data:
        if num % 1000 == 0:
            time.sleep(30)
        elif num % 5000 == 0:
            time.sleep(300)
        num += 1
        # run(id_, manbing_disease_url)
        pool.apply_async(run, args=(id_, manbing_disease_url),)
        num += 1
    pool.close()
    pool.join()