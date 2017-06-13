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
from tools.usermanager import UserManager

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

# um = UserManager(accounts)
# um.start_verify_solution(['1', '2'])
# um.start_verify_solution()
# test()
qm = qm()
qm.load()
# print(len(qm.get_free_problem()))
vs.print_types(qm.get_free_problem())
# execute(['scrapy', 'crawl', 'solutions_spider'])




























