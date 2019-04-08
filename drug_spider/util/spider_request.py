# -*- coding=utf-8 -*-

import requests
import spider_base
import spider_parse
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from requests.exceptions import RequestException
from requests.exceptions import ConnectionError
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import random
import platform
from pyvirtualdisplay import Display
from fake_useragent import UserAgent
import os

# 代理
proxy_url = "http://proxy.httpdaili.com/apinew.asp?text=true&noinfo=true&sl=10&ddbh=145967976925544552"
# proxy_url = "http://proxy.httpdaili.com/a/ip.txt"

# 淘宝
taobao_login_url_pc = "https://login.taobao.com/member/login.jhtml"
taobao_login_url_phone = "https://login.m.taobao.com/login.htm"

# 淘宝账户密码
taobao_user = "13100665135"
taobao_passwd = "lqf123456"


# def dynamic_proxy():
#     """获取代理动态IP地址"""
#     response = request_get_url_no_proxy(proxy_url)
#     proxy_list = response.text.encode("utf-8").split("\r\n")
#     return random.choice(proxy_list)


def dynamic_proxy():
    """获取静态动态代理"""
    with open("proxy", "r") as f:
        proxy_list = (f.readlines())
    return random.choice(proxy_list)


def request_get_url_no_proxy(url):
    """使用get提交请求url不通过代理"""
    # 获取随机的请求头
    ua = UserAgent()
    user_agent = ua.random
    headers = {"User-Agent": user_agent}

    loop = 0
    while True:
        try:
            response = requests.get(url, headers=headers)
        except Exception as e:
            print "第 - {} - 次请求异常".format(loop)
            print(e)
            time.sleep(random.randint(1, 2))
            print "获取代理地址有问题"
            if loop >= 3:
                return False
            loop += 1
            continue
        else:
            return response


def request_get_url(url):
    """使用get提交请求url"""
    # 获取随机的请求头
    ua = UserAgent()
    user_agent = ua.random
    headers = {"User-Agent": user_agent}

    # 获取随机代理
    proxy_ip = dynamic_proxy()
    proxy_list = proxy_ip.split(':')
    proxy_dict = {proxy_list[0]: proxy_list[1]}

    loop = 0
    while True:
        try:
            response = requests.get(url, headers=headers, proxies=proxy_dict)
        except Exception as e:
            print "第 - {} - 次请求异常".format(loop)
            print(e)
            time.sleep(random.randint(1, 2))
            if loop >= 3:
                return False
            loop += 1
            continue
        else:
            return response


def create_chromedriver_on_darwin(is_headless):
    """在darwin系统上创建chromedriver(目前只测试了macos high sierra 10.13.3)"""
    # 获取随机代理
    proxy_ip = dynamic_proxy()
    # 获取随机的请求头
    ua = UserAgent()
    user_agent = ua.random
    # 获取chromedriver路径
    my_sys = platform.system()
    chrome_path = os.getcwd() + "/driver/" + my_sys + "/chromedriver"

    # 开始创建options
    options = webdriver.ChromeOptions()
    options.add_argument('lang=zh_CN.UTF-8')

    # 设置代理
    # options.add_argument('--proxy-server=http://' + proxy_ip)

    # 设置请求头
    options.add_argument('user-agent={}'.format(user_agent))
    if is_headless is True:
        # 设置静默加载
        options.set_headless()

    # 开始创建driver(代理方法1)
    driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=options)
    return driver


def create_firefoxdriver_on_Linux(is_headless):
    """在linux系统上创建firefoxdriver(目前只测试了centOS 6.5)"""
    # 获取随机代理
    proxy_ip = dynamic_proxy()
    # 获取随机的请求头
    ua = UserAgent()
    user_agent = ua.random

    # 获取chromedriver路径
    my_sys = platform.system()
    gecko_path = os.getcwd() + "/driver/" + my_sys + "/geckodriver"

    # 在无图形界面的linux上虚拟化一个显示窗体(is_headless为False可以不用创建)
    display = Display(visible=0, size=(800, 600))
    display.start()

    # 开始创建options
    options = webdriver.FirefoxOptions()
    options.add_argument('lang=zh_CN.UTF-8')
    options.add_argument('--proxy-server=http://' + proxy_ip)
    # 注意：在Firefox上添加请求头的方式和Chrome不一样
    options.set_preference("general.useragent.override", user_agent)
    if is_headless is True:
        # 设置静默加载
        options.set_headless()

    # 在linux上创建driver
    binary = FirefoxBinary(gecko_path)
    driver = webdriver.Firefox(firefox_binary=binary, firefox_options=options)
    return driver, display


def close_selenium_on_darwin(driver):
    """在darwin系统上关闭driver"""
    driver.quit()


def close_selenium_on_linux(driver, display):
    """在linux系统上关闭driver"""
    driver.quit()
    display.stop()


def request_chromedriver_alihealth(driver, url):
    """使用chromedriver请求url(专用于处理阿里健康大药房的手机端口,成功率高)"""
    # 开始请求目标URL
    loop = 0
    while True:

        # driver.start_session(desired_capabilities)

        # 不关闭webdriver动态修改的代理的方法(有问题,目前还不能使用)
        # proxy_ip = dynamic_proxy()
        # proxy = driver.Proxy()
        # proxy.proxy_type = ProxyType.MANUAL
        # proxy.http_proxy = proxy_ip
        # # 将代理设置添加到webdriver.DesiredCapabilities
        # proxy.add_to_capabilities(driver.DesiredCapabilities.CHROME)

        # 不关闭webdriver动态修改请求头的方法还没有找到
        # .....

        try:
            # 不关闭webdriver动态修改的代理的方法(可用)
            proxy_ip = dynamic_proxy()
            proxy = Proxy(
                {
                    'proxyType': ProxyType.MANUAL,
                    'httpProxy': proxy_ip
                }
            )
            desired_capabilities = DesiredCapabilities.CHROME.copy()
            proxy.add_to_capabilities(desired_capabilities)

            driver.set_page_load_timeout(15)
            driver.implicitly_wait(20)
            driver.get(url)

            # 等待请求进度
            time.sleep(random.randint(1, 2))

            # 判断是阿里跳转登录
            if driver.current_url:
                if driver.current_url.startswith("https://login") is True:
                    print "阿里跳转登录"
                    time.sleep(1)
                    driver.quit()
                    return "login"

            # with open("123.html", "w") as f:
            #     f.write(driver.page_source)

            # 判断是阿里弹窗登录
            if driver.current_url:
                if "login.m.taobao.com" in driver.page_source and '关闭' in driver.page_source:
                    print "阿里弹窗登录"
                    driver.find_element_by_xpath("//div[@class='J_MIDDLEWARE_FRAME_WIDGET']//a").click()
                    time.sleep(1)

            # 判断是否是过期商品(过期商品会有弹窗体需要特殊的处理方法来获取)
            if driver.current_url:
                if u"卖光" in driver.page_source:
                    print "此商品已卖光"
                    # 经尝试无效
                    # driver.find_element_by_xpath("//div[@id='downshelf-content']//div[@class='bg']").click()
                    # 经尝试无效
                    # driver.find_element_by_name("downshelf-content").click()
                    # 有效(selenium点击伪元素的方法在这里！！！)
                    driver.find_element_by_css_selector('div.hd>div').click()
                    # script = "return window.getComputedStyle(document.querySelector('#validationError'),':before').getPropertyValue('content')"
                    # driver.execute_script(script)
                    # return False

            # 最后处理各种棘手问题!呵呵
            if u'您查看的宝贝不存在' in driver.page_source:
                print "您查看的宝贝不存在"
                return False

            if u'未连接到互联网' in driver.page_source:
                print "未连接到互联网"
                continue

            # 到此为止,进入一个正常的药品界面,准备开始拿数据
            # 先把浏览器页面滑动到底部,等待商品详情数据的加载
            # driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

            # 拖动到可见的元素去(方法1)
            # driver.execute_script("window.location.hash='#J_mod12';")
            # time.sleep(1)
            # driver.execute_script("window.scrollTo(0, document.body.scrollTop+{});".format(300))
            # driver.execute_script("window.scrollTo(0, {});".format(random.randint(1200, 1400)))

            # 拖动到可见的元素去(方法2)
            # target = driver.find_element_by_id("J_mod12")
            # driver.execute_script("arguments[0].scrollIntoView();", target)

            # 点击元素使商品参数加载
            time.sleep(1)
            # 可能会失效
            # driver.find_element_by_xpath("//div[@id='J_mod12']").click()
            # 可能会失效
            # driver.find_element_by_id('J_mod12').click()
            # driver.find_element_by_css_selector('div.props-content>div').click()
            # driver.find_element_by_xpath("//div[@class='props-content']").click()
            # js_params = "var q=document.getElementById('J_mod12').children[1].children[1].click()"
            # driver.execute_script(js_params)
            # time.sleep(1)
            # 可能会失效
            # driver.find_element_by_xpath("//div[@class='cover-footer']").click()
            # driver.find_element_by_name("div class='cover-footer'").click()
            # driver.find_element_by_class_name('cover-footer').click()

            # time.sleep(1)
            driver.execute_script("window.scrollTo(0,{})".format(random.randint(8000, 9000)))

            # if u'卖光' in html:
            #     print "卖光"
            #     continue

            # 一切结束后等待,防止请求太过频繁
            time.sleep(2)
            # 获取网页源码并返回
            html = driver.page_source

            return html

        except ConnectionError as e:
            print e
            print "连接异常"
            # 出现问题之后极大可能已经被阿里封了,要增大等待时间
            time.sleep(60)
            if loop >= 1:
                return False
            loop += 1
            print "第{}次请求失败".format(loop)
            continue

        except RequestException as e:
            print e
            print "请求异常"
            # 出现问题之后加长延迟时间
            time.sleep(random.randint(1, 2))
            # 请求失败,可能是代理已经过期,立即重新请求
            if loop >= 3:
                return False
            loop += 1
            print "第{}次请求失败".format(loop)
            continue

        except Exception as e:
            print e
            print "其它异常"
            # 出现问题之后加长延迟时间
            time.sleep(random.randint(1, 2))
            # 其它异常,只重复1次
            if loop >= 1:
                return False
            loop += 1
            print "第{}次请求失败".format(loop)
            continue


def request_selenium_alihealth_phone(driver):
    """使用chromedriver处理阿里的登录问题
        专用于处理天猫阿里健康大药房的手机端口"""
    loop = 0
    while True:
        # 不关闭chromedriver动态修改的代理的方法(可用)
        proxy_ip = dynamic_proxy()
        proxy = Proxy(
            {
                'proxyType': ProxyType.MANUAL,
                'httpProxy': proxy_ip
            }
        )
        desired_capabilities = DesiredCapabilities.CHROME.copy()
        proxy.add_to_capabilities(desired_capabilities)

        try:
            driver.set_page_load_timeout(10)  # 手机时间可以设置短
            driver.implicitly_wait(25)
            driver.get(taobao_login_url_phone)

            driver.delete_all_cookies()

            # 输入账号密码
            time.sleep(random.randint(1, 2))
            driver.find_element_by_id("username").send_keys(taobao_user)
            time.sleep(random.randint(1, 2))
            driver.find_element_by_id("password").send_keys(taobao_passwd)

            time.sleep(random.randint(2, 4))

            driver.find_element_by_id("btn-submit").click()

            time.sleep(random.randint(20, 30))

            # 登录成功获取cookies
            cookie = driver.get_cookies()

            return cookie

        except Exception as e:
            print e
            if loop >= 3:
                break
            loop += 1
            print "第{}次请求失败".format(loop)
            continue


def request_selenium_alihealth(driver):
    """
        使用chromedriver处理阿里的登录问题
        (专用于处理天猫阿里健康大药房的WEB端口,
        先开始可以成功,之后成功率极低,必须不定时更换手段)
        处理反爬的手段:
        1:换User-Agent
        2:换代理
        3:使用鼠标模拟人类行为（鼠标移动轨迹每次应该不一样）
        4:输入账号密码的动作应该放慢不应该瞬间完成
        5:定期更换webdriver内核(把不同版本webdriver放在项目目录下)
        6:2次登录的间隔时间不能太短
        7:滑动滑块时应该放慢速度
        8:阿里的验证规则定期更新，下次可能还会出现别的规则,必须不断尝试
    """
    loop = 0
    while True:

        # 不关闭chromedriver动态修改的代理的方法(可用)
        proxy_ip = dynamic_proxy()
        proxy = Proxy(
            {
                'proxyType': ProxyType.MANUAL,
                'httpProxy': proxy_ip
            }
        )
        desired_capabilities = DesiredCapabilities.CHROME.copy()
        proxy.add_to_capabilities(desired_capabilities)

        try:
            driver.set_page_load_timeout(15)
            driver.implicitly_wait(20)
            driver.get(taobao_login_url_pc)
            driver.delete_all_cookies()

            time.sleep(random.randint(1, 2))

            # 鼠标模拟人类滑动
            # 函数已经放弃使用(浪费时间之后好像也不能提高成功率)

            # 点击元素弹出登录框
            QR_button = driver.find_element_by_xpath("//i[@id='J_Quick2Static']")
            QR_button.click()

            # 输入账号密码
            time.sleep(random.randint(1, 2))
            driver.find_element_by_id("TPL_username_1").send_keys(taobao_user)
            time.sleep(random.randint(1, 2))
            driver.find_element_by_id("TPL_password_1").send_keys(taobao_passwd)

            # 等待账密输入
            time.sleep(random.randint(2, 4))

            while True:

                # 处理滑块问题
                scroll_panel = driver.find_element_by_xpath("//*[@id='nc_1_n1z']")

                actions = ActionChains(driver)

                actions.click_and_hold(scroll_panel)

                # 此处的数字可做改动
                actions.move_by_offset(60, 0)
                time.sleep(0.1)
                actions.move_by_offset(60, 0)
                time.sleep(0.1)
                actions.move_by_offset(60, 0)
                time.sleep(0.3)
                actions.move_by_offset(78, 0)

                actions.release().perform()

                # 等待滑动完毕
                time.sleep(random.randint(1, 2))

                text = driver.find_element_by_xpath("//span[@class='nc-lang-cnt']")

                if not text.text.startswith(u'验证通过'):
                    print('滑动失败')
                    # 需要点击刷新按钮
                    # <a href="javascript:noCaptcha.reset(1)">刷新</a>
                    refresh_button = driver.find_element_by_xpath("//a[@href='javascript:noCaptcha.reset(1)']")
                    refresh_button.click()
                    loop += 1
                    continue
                elif str('点击') in text.text:

                    print('滑动成功')
                    # 点击登录按钮
                    login_button = driver.find_element_by_xpath("//button[@id='J_SubmitStatic']")
                    login_button.click()

                    # 成功等待
                    time.sleep(random.randint(1, 2))

                    # 登录成功获取cookie
                    cookie = driver.get_cookies()

                    return cookie

        except Exception as e:
            print e
            if loop >= 3:
                break
            loop += 1
            print "第{}次请求失败".format(loop)
            continue
