# -*- coding:utf-8 -*-

import re
import json
import sys
import spider_db
import xlwt
import xlrd
from lxml import etree

reload(sys)
sys.setdefaultencoding('utf8')

"""
目前还有问题
问题1:多个sheet怎么办？
问题2:字段名称怎么命名？
"""


def parse_excel_to_sql(sql_name, table_name, excel_name):
    """把EXCEL转化成SQL"""

    try:
        # 打开excel读取数据
        data = xlrd.open_workbook(excel_name)
        # 创建数据库连接
        conn = spider_db.db_conn(sql_name)
    except Exception as e:
        print "参数异常"
    else:
        # 获取工作表
        table_list = data.sheets()

        for table in table_list:
            # 获取行列的值
            rows = table.nrows
            cols = table.ncols
            # 获取整行和整列的值(返回list)
            # table.row_values(i)
            # table.col_values(i)
            # 遍历数据
            for row in xrange(rows):
                for col in xrange(cols):
                    val = table.cell(row, col).value
                    
                    sql = "insert into {}() values() {}".format(table_name)
                    cur = spider_db.dbExecu(sql, conn)


def parse_sql_to_excel(sql_name, table_name, excel_name):
    """把SQL转化成EXCEL"""

    try:
        # 创建数据库连接
        conn = spider_db.db_conn(sql_name)
        # 查询需要转化的数据表
        sql = "select * from {}".format(table_name)
        cur = spider_db.dbExecu(sql, conn)
    except Exception as e:
        print "数据库连接异常"
    else:
        # 创建Excel
        workbook = xlwt.Workbook(encoding='ascii')
        worksheet = workbook.add_sheet(table_name)

        # 往单元格内写数据
        sql_data = cur.fetchall()
        for index_outer, data in enumerate(sql_data):
            for index_inner, da in enumerate(data):
                worksheet.write(index_outer, index_inner, label=str(da))

        # 保存excel
        workbook.save(excel_name)
        # 关闭数据库连接
        spider_db.db_close(conn)


def parse_json_to_dict(json_data):
    """把JSON转化成DICT"""
    return json.loads(json_data, encoding='utf-8')


def parse_dict_to_json(data):
    """把DICT转化成JSON"""
    return json.dumps(data, ensure_ascii=False).decode('utf8')


def parse_list_to_json(data):
    """把LIST转化成JSON"""
    jsondt = []
    jsondic = {}
    for index in range(len(data)):
        jsondt.append(index)
    jsondic = dict(zip(jsondt, data))
    return json.dumps(jsondic, ensure_ascii=False).decode('utf8')


def parse_json_to_list(data):
    """把JSON转化成LIST"""
    # 第1步:取出字典
    list_tupe = data.items()
    list_new = list()

    # 第2步:遍历字典中的元组
    for li in list_tupe:
        list_new.append(li[0])
        list_new.append(li[1])
    return list_new


def judge_url_login(url):
    """判断是否跳转到淘宝的登录界面"""
    pattern = re.compile(r'^http?://login*')
    res = pattern.match(url)
    if res is not None:
        return True


def judge_url_expire(content):
    """判断是否是过期商品(适用于手机端界面)"""
    html = etree.HTML(content)
    text = html.xpath("//div[@id='s-downshelf']//div[@class='hd']/text()")
    for te in text:
        if u'卖光' in te:
            return True


def parse_url_http(url):
    """过滤URL给加上HTTP前缀"""
    if url is None and url == 'None':
        return url
    pattern = re.compile(r'^http:*')
    res = pattern.match(url)
    if res is None:
        url = 'http:' + url
        return url
    else:
        return url


def contentsub(info=''):
    """去除内容中的HTML标签"""
    re_h = re.compile('</?\w+[^>]*>')  # HTML标签
    re_nbsp = re.compile(' ')
    re_comment = re.compile('<!--[^>]*-->')  # HTML注释
    re_br = re.compile('<br\s*?/?>')  # 处理换行
    # 去掉多余的空行
    info = re_h.sub('', info)
    info = re_br.sub('\n', info)
    info = re_comment.sub('', info)
    info = re_nbsp.sub('', info)
    blank_line = re.compile('\n+')
    info = blank_line.sub('\n', info)
    info = info.replace('&nbsp;', '').replace('\n', '')
    return info


def parse_url_for_info_href(base_url, content):
    """将content 内的 a 标签替换"""
    res_href = r"""href=["']?([^"']+)["']?[^>]*>[^<]"""
    hrefs = re.findall(res_href, content, re.S | re.M)
    for url in hrefs:
        if not url.startswith('h'):
            url_replace = base_url + url
            content = content.replace(url, url_replace)
    return content


def parse_url_for_info_img(base_url, content):
    """将 content 内的 img 标签替换"""
    res_imgs = r"""src=["']?([^"']+)["']?[^>]*>"""
    srcs = re.findall(res_imgs, content, re.S | re.M)
    for url in srcs:
        if not url.startswith('h'):
            url_replace = base_url + url
            content = content.replace(url, url_replace)
    return content


def parse_url_for_info_line_style(content):
    """将 content 内的行间样式和 style 样式去掉"""
    res_line = r"""(style=.*?)>|(class=.*?)>"""
    for line in re.findall(res_line, content):
        content = re.sub(res_line, '>', content, re.I)
    return content


def parse_url_for_info_video(label, content):
    """判断页面内是否含有 video 标签"""
    res_video = r"""<%s.*?>""" % label
    rr = re.findall(res_video, content)
    if len(rr) != 0:
        return True
    else:
        return False

if __name__ == '__main__':
    # 仅仅用于测试函数
    # parse_sql_to_excel('gaoji_drug_data', 'auth_permission', 'demo.xls')
    parse_excel_to_sql('gaoji_drug_data', 'demo', 'demo.xls')
