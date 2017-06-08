# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-06 13:33:57
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-07 19:48:46

# data source directory has already been set in main.py

from os.path import join

# data path
DATA_BASE_PATH = "data/"
DATA_META_PATH = join(DATA_BASE_PATH, "questions_meta.json")
DATA_CONTENT_PATH = join(DATA_BASE_PATH, "question_content")
DATA_SOLUTION_PATH = join(DATA_BASE_PATH, "question_solution")

# format string
NEW_LINE = '--newline--'
TAB = '--tab--'

# debug setting
DEBUG = True