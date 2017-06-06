# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-05 13:36:10
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-06 16:20:21


from scrapy.cmdline import execute

import sys
import os
from util.Data import test
# print(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# print(sys.path)
# from util.data_settings import *
# with open(DATA_META_PATH, 'r') as f :
#     print(f.read())

execute(["scrapy","crawl","solutions_spider"])
# test()