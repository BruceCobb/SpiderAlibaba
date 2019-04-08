# -*- coding=utf-8 -*-

import sys
import spider_request
import spider_parse
import spider_db
from lxml import etree
import MySQLdb
from multiprocessing import Lock
import multiprocessing
import thread
import threading
import random
import time
import os
import Queue

reload(sys)
sys.setdefaultencoding('utf8')


class alihealth():

    def __init__(self, lock):

        if os.getenv('CONF_ENVMODE') == "test":
            self.user = "root"
            self.passwd = ""
        elif os.getenv('CONF_ENVMODE') == "prod":
            self.user = "root"
            self.passwd = "qwertyuiopQ123!@#"
        elif os.getenv('CONF_ENVMODE') == "device":
            self.user = "root"
            self.passwd = "root"

        self.db_name = "gaoji_drug_data"

        self.lock = lock

        self.base_reg = "//div[@class='cat-item'][1]//div[@class='pan-item-body']/a/text()"

        self.base_search_list_reg = "//a[@class='J_ClickStat']/@href"

        self.base_ajax_url = "https://maiyao.liangxinyao.com/i/asynSearch.htm?_ksTS=1526295219280_121&callback=jsonp122&mid=w-15153317282-0&wid=15153317282&path=/category.htm&spm=a1z10.5-b-s.w11755005-15153317280.7.vYLhd8&search=y&parentCatName=%B2%B9%D2%E6%B0%B2%C9%F1&catName=%B2%B9%C9%F6&parentCatId=1250009498&acm=lb-zebra-199393-2258356.1003.4.1981841&scm=1003.4.lb-zebra-199393-2258356.OTHER_14994872681511_1981841&catId=1276249451"

        self.login = "https://login.taobao.com/member/login.jhtml?redirectURL=https://www.taobao.com/"

        self.base_alihealth = "https://www.liangxinyao.com/?scene=taobao_shop"

        self.base_search_taobao = "https://s.taobao.com/search?q=阿里健康大药房 {}&imgfile=&js=1&stats_click=search_radio_all:1&initiative_id=staobaoz_20180516&ie=utf8&bcoffset=4&p4ppushleft=1,48&ntoffset=4&s={}"

        self.base_search_tmall = "https://list.tmall.com/search_shopitem.htm?user_id=2928278102&cat=2&spm=875.7931836/B.a2227oh.d100&oq=阿里健康大药房&from=mallfp..pc_1_searchbutton&ds=1&stype=search"

    def _count_page(self, count):
        """根据给定的参数返回正确的页面"""
        count_sign = (count - 1) * 44
        return self.base_search_taobao.format("", str(count_sign))

    def _parse_app_drug(self, content, url):

        with open("drug_data{}.html".format(str(random.randint(1, 10000))), 'w') as f:
            f.write(content)

        html = etree.HTML(content)

        try:
            # drug_params_name_list = html.xpath("//div[@class='cover-body']//th/text()")
            #
            # drug_params_value_list = html.xpath("//div[@class='cover-body']//td/text()")
            #
            # drug_params = dict(zip(drug_params_name_list, drug_params_value_list))
            #
            # img_small = html.xpath("//div[@class='scroller preview-scroller']//a[@class='item']/img/@src")

            # img_details = html.xpath("//div[@class='mui-custommodule-item unloaded']/img/@data-ks-lazyload")

            img_details = html.xpath("//div[@id='description']//img/@src")
            # 规则可能出现不一样
            # if len(img_details) == 0:
            #     img_details = html.xpath("//section[@id='s-desc']//img/@src")
            #     if len(img_details) == 0:
            #         img_details = ['None']
            # 处理图片的链接并转化成正确的格式
            # for index, img in enumerate(img_small):
            #     img_small[index] = spider_parse.parse_url_http(img)
            #
            # # 处理图片的链接并转化成正确的格式
            # for index, img in enumerate(img_details):
            #     img_details[index] = spider_parse.parse_url_http(img)
            #
            # drug_params = spider_parse.parse_dict_to_json(drug_params)
            # img_small = spider_parse.parse_list_to_json(img_small)
            # img_details = spider_parse.parse_list_to_json(img_details)

            print img_details

            input()

            # drug_data = {'url': url, 'drug_params': drug_params, 'img_small': img_small, 'img_details': img_details}

            # return drug_data
        except Exception as e:
            print e
            return False

        # return drug_data

    def _save_app_data(self, drug_data):
        """持久化数据"""
        conn = spider_db.db_conn(db=self.db_name, user=self.user, passwd=self.passwd)
        sql = """update alihealth_app set img_details='{}' where drug_url_app='{}';""" \
            .format(MySQLdb.escape_string(drug_data['img_details']),
                    MySQLdb.escape_string(drug_data['url']))

        spider_db.dbExecu(sql, conn)
        spider_db.db_close(conn)

    def _details_page(self, a, b):
        """根据给定的参数返回正确的页面"""
        conn = spider_db.db_conn(db="gaoji_drug_data")
        sql = """select drug_url_app, drug_params, img_small, img_details from alihealth_app where img_details='{}' limit %s, %s;""" % (a, b)

        cur = spider_db.dbExecu(sql, conn)
        return cur

    def _search_page(self, count):
        """根据给定的参数返回正确的详细搜索页面"""
        global url_sign
        for sign in url_sign:
            count_sign = (count - 1) * 44
            return self.base_search_taobao.format(str(sign), str(count_sign))

    def _parse_drug_list(self, content):
        html = etree.HTML(content)
        url_list = html.xpath(self.base_search_list_reg)

        # 过滤URL
        for index, url in enumerate(url_list):
            url_list[index] = spider_parse.parse_url_http(url)

        # 判断爬虫是否结束
        if self._judge_spider_ending(content) is False:
            return False

        return url_list

    def _parse_drug(self, content):

        # print content
        html = etree.HTML(content)

        try:
            drug_name = html.xpath('//h1[@data-spm="1000983"]/text()')[0].strip()

            drug_params = self._parse_drug_params(html)
            img_small, img_details = self._parse_drug_img(html)

            # print type(img_details)
            # print img_details

            drug_data = {'drug_name': drug_name,
                         'drug_params': drug_params,
                         'img_small': img_small,
                         'img_details': img_details}

            return drug_data
        except Exception as e:
            print e
            return False

    def _parse_drug_params(self, html):
        """处理获取到的药品信息，返回JSON"""
        drug_params_name = html.xpath('//ul[@id="J_AttrUL"]/li/text()')

        name_list = []
        for name in drug_params_name:
            name_list.append(name.split(u':')[0].strip())

        drug_params_value = html.xpath('//ul[@id="J_AttrUL"]/li/@title')

        value_list = []
        for value in drug_params_value:
            value_list.append(value.strip())

        drug_params = dict(zip(name_list, value_list))

        drug_params = spider_parse.parse_dict_to_json(drug_params)

        return drug_params

    def _parse_drug_img(self, html):
        """处理获取到的药品图片，返回JSON"""
        img_small = html.xpath('//ul[@id="J_UlThumb"]//img/@src')
        for index, img in enumerate(img_small):
            img_small[index] = spider_parse.parse_url_http(img)

        # img_middle = html.xpath('//div[@style="position:relative;width:0;height:0;overflow:hidden;"]/img/@src')
        img_details = html.xpath('//div[@id="description"]//img/@src')
        for index, img in enumerate(img_details):
            img_details[index] = spider_parse.parse_url_http(img)

        img_small = spider_parse.parse_list_to_json(img_small)
        img_details = spider_parse.parse_list_to_json(img_details)

        return img_small, img_details

    def _judge_spider_ending(self, content):
        """判断爬虫是否结束"""
        html = etree.HTML(content)
        judge = html.xpath('//div[@class="item-not-found"]//text()')
        for ju in judge:
            if u'未找到' in ju:
                print "未找到"
                return False

    def _duplicate_removal(self, url_list):
        """URL去重"""
        conn = spider_db.db_conn(db=self.db_name, user=self.user, passwd=self.passwd)

        duplicate_list = list(url_list)
        print "获取到的链接为{}个".format(len(url_list))

        for url in duplicate_list:
            sql = """select drug_url from alihealth_drug where drug_url='{}';""".format(url)
            cur = spider_db.dbExecu(sql, conn)
            if cur.fetchone() is not None:
                print "{} was duplicate".format(url)
                url_list.remove(url)

        spider_db.db_close(conn)
        print "去重后的链接为{}个".format(len(url_list))

        return url_list

    def _save_data(self, drug_data):
        """持久化数据"""
        conn = spider_db.db_conn(db=self.db_name, user=self.user, passwd=self.passwd)
        sql = """insert into alihealth_drug values(0, "{}", "{}", "{}", "{}", "{}");""".\
            format(MySQLdb.escape_string(drug_data['drug_url']),
                   MySQLdb.escape_string(drug_data['drug_name']),
                   MySQLdb.escape_string(drug_data['drug_params']),
                   MySQLdb.escape_string(drug_data['img_small']),
                   MySQLdb.escape_string(drug_data['img_details']))

        spider_db.dbExecu(sql, conn)
        spider_db.db_close(conn)

    def alihealth_run(self, a, b):

        # 分析出中西药品的所有url,返回url列表
        # global url_sign
        # content = spider_request.request_url(self.base_alihealth)
        # html = etree.HTML(content)
        # url_sign = html.xpath(self.base_reg)

        cur = self._details_page(a, b)
        driver = spider_request.create_chromedriver_on_darwin(False)

        sign = 0
        while True:

            # 每次请求延迟,避免重复加载
            time.sleep(random.randint(1, 2))

            print os.getpid()

            print "第1步:判断上一次请求是否有异常"
            # lock.acquire()

            if sign == 0:
                data = cur.fetchone()
            elif sign > 3:
                sign = 0
                continue
            if data is None:
                print "爬虫结束"
                break
            # lock.release()

            print "第2步:获取每一个的药品数据"
            url = data[0]
            print "链接为{}".format(url)
            lock.acquire()
            content = spider_request.request_chromedriver_alihealth(driver, url)
            lock.release()
            # 第2步失败处理
            if content == "login":
                driver = spider_request.create_chromedriver_on_darwin(False)
            if content is False:
                # if sign > 3:
                #     sign = 0
                #     continue
                # sign += 1
                sign = 0
                continue

            print "第3步:根据药品链接获取每一页的药品详情"
            drug_data = self._parse_app_drug(content, url)
            # 第3步失败处理
            if drug_data is False:
                print "spider was ending"
                break
            elif len(drug_data) == 0:
                # sign += 1
                sign = 0
                continue

            print "第4步:持久化数据"
            self._save_app_data(drug_data)
            # 准备开始下一次循环
            sign = 0

        # 结束工作
        spider_request.close_selenium_on_darwin(driver)


if __name__ == '__main__':
    lock = Lock()
    ali = alihealth(lock)
    p1 = multiprocessing.Process(target=ali.alihealth_run, args=(0, 5, ))
    p2 = multiprocessing.Process(target=ali.alihealth_run, args=(5, 5,))
    p1.start()
    time.sleep(1)
    p2.start()

    p1.join()
    p2.join()

    # 多进程爬虫(有问题)
    # lock = Lock()
    # ali = alihealth(lock)
    # queue = multiprocessing.Queue()
    # # 获取需要爬取的url游标
    # while True:
    #     data = cur.fetchone()
    #     if data is None:
    #         break
    #     queue.put(data[0])

    # 创建多进程池
    # pool = multiprocessing.Pool(multiprocessing.cpu_count())
    # pool.apply_async(ali.alihealth_run, (queue, ))
    # # pool.map(ali.alihealth_run, cur)
    # pool.close()
    # pool.join()



