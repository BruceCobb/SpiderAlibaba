# -*- coding:utf-8 -*-

import random
import requests
import time
from fake_useragent import UserAgent

import sys
reload(sys)
sys.setdefaultencoding('utf8')


def random_header():
    """获取不同的请求头(返回字典格式)"""
    browser = ['chrome', 'firefox']
    headers = {"User-Agent": getattr(UserAgent(), str(random.choice(browser)))}
    return headers


def sleeping(*kw):
    """执行不同的延时计划"""
    if kw[0] == "random":
        time.sleep(random.randint(kw[1], kw[2]))
    elif kw[0] == "decimal":
        time.sleep(0.5)
    elif kw[0] == "normal":
        time.sleep(1)
    elif kw[0] == "except":
        time.sleep(2)


def generate_url(url, *kw):
    """根据参数填充URL"""
    for k in kw:
        url = url.format(str(k))
    return url
