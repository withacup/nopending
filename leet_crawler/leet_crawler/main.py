# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-05 13:36:10
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-09 15:36:31


from scrapy.cmdline import execute

import sys
import os
from util.Data import QuestionSolutionService as qs
from util.leet_login import test
# from util.Data import test
# print(os.path.dirname(os.path.abspath(__file__)))


# print(sys.path)
# from util.data_settings import *
# with open(DATA_META_PATH, 'r') as f :
#     print(f.read())
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# execute(["scrapy","crawl","solutions_spider"])
# execute(["scrapy","crawl","test_case_spider"])
# test()
#




# print('hello world')
# print('hello world')

# for solu in qs.read_solution('1', qs.PYTHON):
#     print(solu)
# for solu in qs.read_solution('474', qs.CPP):
#     print(solu)
# for solu in qs.read_solution('551', qs.CPP):
#     print(solu)


# test()

from util.leet_login import User

u1 = User(account='tyang8@stevens.edu', password='yangtianxiao')
u1.login()


# from concurrent.futures import ThreadPoolExecutor
#
# import time
# def sleep_print(num):
#     time.sleep(1)
#     return num
#
# with ThreadPoolExecutor(max_workers=10) as executor:
#     # future = executor.submit(pow, 323, 1235)
#     workers = []
#     for i in range(10):
#         workers.append(executor.submit(sleep_print, i))
#     for worker in workers:
#         print(worker.result())





























