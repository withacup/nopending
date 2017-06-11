# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-05 13:36:10
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-10 23:45:50


from scrapy.cmdline import execute

import sys
import os
from util.Data import QuestionSolutionService as qs
from util.Data import QuestionMeta as qm
from util.Data import VerifiedSolutionService as vs

import queue
import time

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
# test()


from concurrent.futures import ThreadPoolExecutor
#
# import time
# def sleep_print(num):
#     time.sleep(1)
#     return num
#
qm = qm()
qm.load()
problem_waiting_queue =  queue.Queue()
# problem_waiting_queue.put(1)
# problem_waiting_queue.put(2)
for problem_id, problem_meta in qm.meta_dict.items():
    if not problem_meta['paid_only']:
        problem_waiting_queue.put(problem_id)

Users = [
    User(account='txyang93@gmail.com', password='yangtianxiao'),
    User(account='tyang8@stevens.edu', password='yangtianxiao'),
    User(account='leetcode0@gmail.com', password='yangtianxiao'),
    User(account='leetcode12@gmail.com', password='yangtianxiao'),
    User(account='leetcode22@gmail.com', password='yangtianxiao'),
    User(account='leetcode32@gmail.com', password='yangtianxiao'),
    User(account='450055865@qq.com', password='yangtianxiao'),
    User(account='it_is_for_mxd@163.com', password='yangtianxiao'),
    User(account='leetremindercomfirm@gmail.com', password='yangtianxiao'),
    User(account='newproblemreminder@gmail.com', password='yangtianxiao'),
]

def print_problem_left():
    while not problem_waiting_queue.empty():
        time.sleep(10)
        print('--->> number of question left: {0}'.format(problem_waiting_queue.qsize()))

def login_submit(user):
    user.login()
    while not problem_waiting_queue.empty():
        start_time = time.time()

        problem_id = problem_waiting_queue.get()
        solutions = qs.read_solution(problem_id=problem_id, l_types=[qs.JAVA, qs.CPP, qs.PYTHON])

        for solution_code, l_type in solutions:
            submission_id = user.submit_solution(problem_id=problem_id, l_type=l_type, solution_code=solution_code)

            res, status_code = user.analyse_submission(submission_id)

            time_consumed = time.time() - start_time
            if time_consumed < 11:
                time.sleep(11 - time_consumed)

            if status_code == 1:
                vs.load_solution_to_problem(problem_id, solution_code=solution_code, l_type=l_type, total_cases=res['total_testcases'])
                vs.save_problem(problem_id)
                break

    return "User {0} submit {1} submissions, {2} accepted, {3} failed".format(user.username, str(user.get_total_submission()), str(user.get_total_accpted()), str(user.get_total_failed()))

start_time = time.time()
with ThreadPoolExecutor(max_workers=11) as executor:
    workers = []
    for i in range(10):
        workers.append(executor.submit(login_submit, Users[i]))
    executor.submit(print_problem_left)

    for worker in workers:
        print(worker.result())

# vs.save_all()

print("total time consumed: {0}".format(time.time() - start_time))





























