# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-08 11:33:12
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-08 12:02:04
import re

NEW_LINE = '--newline--'
TAB = "--tab--"

'''
    format python code with --newline-- and --tab-- escape
'''
def format_python(code):

    lines = code.split(NEW_LINE)
    pre_fix = ""
    format_res = []
    for line in lines:
        new_line = pre_fix + line
        format_res.append(new_line)
        # indent all line below the class definition
        if re.match('^class', line):
            pre_fix = TAB
    return NEW_LINE.join(format_res)