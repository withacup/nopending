# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-05 13:36:10
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-11 19:23:18


from scrapy.cmdline import execute

import sys
import os
from util.questionsolutionservice import QuestionSolutionService as qs
from util.questionmeta import QuestionMeta as qm
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

vs.modify_solution([1])
#qm = qm()
#qm.load()
#vs.print_types(qm.get_free_problem())
# qm.load()
# um = UserManager(accounts=accounts)
# um.start_verify_solution(problem_ids=qm.get_free_problem(), priority=[vs.JAVA, vs.CPP, vs.PYTHON])
# for _id in qm.get_free_problem():
#     print(vs.get_verified_type(problem_id=_id))
import json

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




























