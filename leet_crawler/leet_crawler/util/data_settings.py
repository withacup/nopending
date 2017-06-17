# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-06 13:33:57
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-13 22:26:24

# data source directory has already been set in main.py

from os.path import join

# data path
DATA_BASE_PATH = "data/"
DATA_META_PATH = join(DATA_BASE_PATH, "questions_meta.json")
DATA_CONTENT_PATH = join(DATA_BASE_PATH, "question_content")
DATA_SOLUTION_PATH = join(DATA_BASE_PATH, "question_solution")
VERIFIED_SOLUTION_PATH = join(DATA_BASE_PATH, 'verified_solution')
TEST_CASES_PATH = join(DATA_BASE_PATH, 'test_cases')
COOKIE_PATH = join(DATA_BASE_PATH, "session_cookie")
DATA_TMP_PATH = join(DATA_BASE_PATH, 'tmp')

# format string
NEW_LINE = '--newline--'
TAB = '--tab--'

# debug setting
DEBUG = True
REFRESH_META = False

# leetcode account
USER = 'tyang8@stevens.edu'
PASS = 'yangtianxiao'
AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"

# global variables
MAX_TOPIC = 5