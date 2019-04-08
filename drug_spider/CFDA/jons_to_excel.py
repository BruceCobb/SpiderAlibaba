# -*- coding:utf-8 -*-

import json
import pandas
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')


if __name__ == '__main__':

    # json_data = json.loads("json_demo.json")

    pandas.read_json("json_demo.json").to_excel("output13.xlsx")
