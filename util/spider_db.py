# -*- coding:utf-8 -*-

import logging
import MySQLdb

# reload(sys)
# sys.setdefaultencoding('utf8')


def db_conn(db, host='127.0.0.1', port=3306, user='root', passwd='root', charset='utf8'):
    conn = MySQLdb.connect(
        host=host,
        port=port,
        user=user,
        passwd=passwd,
        db=db,
        charset=charset
    )
    return conn


def db_close(conn):
    conn.close()


def dbExecu_list(sql_list, conn):
    """执行多个SQL语句返回游标列表"""
    cur_list = list()
    for sql in sql_list:
        if sql == '' or sql is None:
            return False
        try:
            cur = conn.cursor()
            cur.execute(sql)
            cur_list.append(cur)
        except Exception as e:
            logging.error(e)
            conn.rollback()
        else:
            conn.commit()
    return cur_list


def dbExecu(sql, conn):
    """执行单个SQL并返回游标"""
    try:
        cur = conn.cursor()
        cur.execute(sql)
    except Exception as e:
        logging.error(e)
        conn.rollback()
    else:
        conn.commit()
        return cur
