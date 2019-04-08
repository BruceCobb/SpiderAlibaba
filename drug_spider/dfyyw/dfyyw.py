# -*- coding: utf-8 -*-

from multiprocessing import Pool
from HTMLParser import HTMLParser
import multiprocessing
import sys
import os
import time
import json

from spider_db import *
from spider_parse import *
from spider_request import *


reload(sys)
sys.setdefaultencoding('utf-8')

base_url = 'http://www.yaozs.com/sms'
db = MySQLdb.connect(host='localhost', user='root', passwd='root', db='gaoji_drug_data', port=3306, charset='utf8')


def insert_(url, data):
    cur = db.cursor()
    sql = \
        """
            insert ignore into dfyyw (url, json_file) values ('{}', '{}')
        """.format(
            MySQLdb.escape_string(url),
            MySQLdb.escape_string(data))
    try:
        cur.execute(sql)
        # print sql
    except Exception as e:
        print "进程{}持久化异常!!!!!!\n".format(os.getpid())
        print e
    else:
        db.commit()
        print "进程{}存储成功\n".format(os.getpid())


def run(page):
    url = base_url + str(page + 1) + '/'
    while True:
        print "进程{}URL{}\n".format(os.getpid(), url)

        response = request_get_url(url)
        response.encoding = 'utf-8'
        html = etree.HTML(response.text)

        try:
            html_dict = dict()
            html_node = html.xpath("//article[@class='panel-detail']//div[@class='row']")

            for html in html_node:
                data = etree.tostring(html)
                data = HTMLParser().unescape(data)
                data = contentsub(data)
                data_list = data.split("：")
                html_dict[data_list[0]] = data_list[1]

            if len(html_dict) == 0:
                continue

            result = json.dumps(html_dict, ensure_ascii=False, encoding='utf-8')

        except Exception as e:
            print "解析失败，result = 'fail'\n"
            result = "null"

        else:
            # 持久化数据
            insert_(url=url, data=result)
            time.sleep(0.5)
            break


if __name__ == "__main__":
    pool = Pool(2)

    for page in range(0, 114444):
        pool.apply_async(func=run, args=(page,), )

    pool.close()
    pool.join()

# drug_list = [985,
#     986,
#     987,
#     988,
#     989,
#     990,
#     991,
#     992,
#     993,
#     994,
#     995,
#     996,
#     997,
#     998,
#     999,
#     1000,
#     1001,
#     1002,
#     1003,
#     1004,
#     1005,
#     1006,
#     1007,
#     1008,
#     1009,
#     1010,
#     1011,
#     1012,
#     1013,
#     1014,
#     1015,
#     2942,
#     2943,
#     2944,
#     2945]