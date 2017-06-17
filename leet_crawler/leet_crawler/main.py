# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-05 13:36:10
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-16 16:38:56

from scrapy.cmdline import execute

import sys, os, json
from util.questionsolutionservice import QuestionSolutionService as qs
from util.questionmeta import QuestionMeta as qm
from util.data_settings import *
from util.verifiedsolutionservice import VerifiedSolutionService as vs
from util.questioncontent import QuestionContent as qc
from tools.usermanager import UserManager
from util.leet_login import User

accounts = [
    ['txyang93@gmail.com', 'yangtianxiao'],
    ['tyang8@stevens.edu', 'yangtianxiao'],
    ['leetcode0@gmail.com', 'yangtianxiao'],
    ['leetcode12@gmail.com', 'yangtianxiao'],
    ['leetcode22@gmail.com', 'yangtianxiao'],
    ['leetcode32@gmail.com', 'yangtianxiao'],
    ['450055865@qq.com', 'yangtianxiao'],
    ['it_is_for_mxd@163.com', 'yangtianxiao'],
    ['leetremindercomfirm@gmail.com', 'yangtianxiao'],
    ['newproblemreminder@gmail.com', 'yangtianxiao'],
]
qm = qm()
qm.load()
from os import listdir
# import os
tough_guy = ['391', '575', '141', '142']

def get_not_modified():
    modified = listdir(TEST_CASES_PATH)
    return list(filter(lambda _id: (_id + '.txt') not in modified, qm.get_free_problem()))

# print(get_not_modified())
# for code in vs.modify_solution(qm.get_free_problem()):

# vs.print_types(qm.get_free_problem())
# qm.load()
um = UserManager(accounts=accounts)
um.start_verify_modified_solution(list(filter(lambda _id: vs.get_verified_type(_id) == vs.JAVA and _id not in ['391', '575'], get_not_modified())))
# um.start_verify_modified_solution([594, 4, 452, 525, 84, 219, 135, 442, 575, 463, 391])
# um.start_verify_modified_solution([493])
# um.start_verify_solution(problem_ids=qm.get_free_problem(), priority=[vs.JAVA, vs.CPP, vs.PYTHON])

# print(vs.get_verified_code(315))
# vs.get_verified_code()
# print(vs.get_modified_solution([2], end=1, l_type=vs.JAVA, offset=0)[0][0])
# for _id in qm.get_free_problem():
#     print(vs.get_verified_type(problem_id=_id))

# user = User(account='txyang93@gmail.com', password='yangtianxiao')
# user.login()
# while True:
    # code = input("code = ")
    # _id = user.submit_solution(problem_id=529, l_type=vs.JAVA, solution_code=code)
    # print(user.analyse_submission(_id)[0]['std_output'])
# um = UserManager(accounts)
# um.start_verify_solution(['1', '2'])
# um.start_verify_solution()
# test()

# counter = 0
# print(vs.get_total_cases(529))
# for _id in qm.get_free_problem():
    # _qc = qc()
    # _qc.load(_id)
    # print(_qc.get_script(qc.JAVA))
    # print(vs.get_raw_verified_code(_id))
    # if vs.get_total_cases(_id) > 200:
        # counter += 1
        # print(_id + " " + str(vs.get_total_cases(_id)))
# print(counter)


# print(len(qm.get_free_problem()))
# vs.print_types(qm.get_free_problem())
# print(vs.get_verified_code(31))
# execute(['scrapy', 'crawl', 'solutions_spider'])




























