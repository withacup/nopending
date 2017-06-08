# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-05 13:36:10
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-08 13:46:48


from scrapy.cmdline import execute

import sys
import os
from util.Data import QuestionSolutionService as qs
from util.Data import test
# print(os.path.dirname(os.path.abspath(__file__)))


# print(sys.path)
# from util.data_settings import *
# with open(DATA_META_PATH, 'r') as f :
#     print(f.read())
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# execute(["scrapy","crawl","solutions_spider"])
# print('hello world')

# for solu in qs.read_solution('1', qs.PYTHON):
#     print(solu)
# for solu in qs.read_solution('474', qs.CPP):
#     print(solu)
for solu in qs.read_solution('474', qs.PYTHON):
    print(solu)


# test()