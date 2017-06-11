# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-06 13:33:57
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-10 22:05:47

# data source directory has already been set in main.py

from os.path import join

# data path
DATA_BASE_PATH = "data/"
DATA_META_PATH = join(DATA_BASE_PATH, "questions_meta.json")
DATA_CONTENT_PATH = join(DATA_BASE_PATH, "question_content")
DATA_SOLUTION_PATH = join(DATA_BASE_PATH, "question_solution")
VERIFIED_SOLUTION_PATH = join(DATA_BASE_PATH, 'verified_solution')
COOKIE_PATH = join(DATA_BASE_PATH, "session_cookie")
DATA_TMP_PATH = join(DATA_BASE_PATH, 'tmp')

# format string
NEW_LINE = '--newline--'
TAB = '--tab--'

# debug setting
DEBUG = False

# leetcode account
USER = 'tyang8@stevens.edu'
PASS = 'yangtianxiao'
AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"

# global variables
MAX_TOPIC = 5