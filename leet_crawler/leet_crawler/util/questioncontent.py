# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-12 20:28:36
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-12 20:30:26

import re
import html  # for decode html escaped string

from util.common import *

class QuestionContent:

    # This class cannot be re-loaded when not saved
    is_loaded_table = {}

    CPP = 'cpp'
    JAVA = 'java'
    PYTHON = 'python'

    reg = '.*---{0}_BEGIN---\n(.*?)\n---{0}_END---.*'
    sep = '---{0}_BEGIN---\n{1}\n---{0}_END---\n'

    def __init__(self):
        self.f_text = ""
        self.content = ""
        self.script_arr = []
        self.is_locked = False
        self.problem_id = None

    def __str__(self):
        return str(self.problem_id) + ".txt"

    def load(self, problem_id, new=False):

        if self.problem_id is not None:
            elog("Duplicate QuestionContent Loading Error", "question content with id: {0} is trying to load again".format(self.problem_id)) 

        if self.problem_id in QuestionContent.is_loaded_table and QuestionContent.is_loaded_table[self.problem_id]:
            elog("Duplicate QuestionContent Loading Error", "question content is trying to load before other object save their data")

        # only read content when the problem content is not new content
        if not new:
            try:
                # this has to be str(problem_id), because self.problem_id is the identifier for this object,
                # I have to set it at the end of the function
                with open(join(DATA_CONTENT_PATH, str(problem_id) + ".txt"), 'r') as content:
                    text = content.read()
                    if text == "locked":
                        print('problem: {0} is locked'.format(self.problem_id))
                        self.is_locked = True
                    self.f_text = text
            except IOError as err:
                elog(err, "load question: {0} content failed".format(self.problem_id))

        self.problem_id = str(problem_id)
        QuestionContent.is_loaded_table[self.problem_id] = True

    def get_content(self):
        if self.is_locked:
            return "locked"
        if self.content == "":
            if self.problem_id is None:
                elog('Get Content Error', 'problem has not been loaded yet')
            self.content = self.parse_content(self.f_text)
        return self.content

    """
        This method return a encoded string as script
    """
    def get_script(self, s_type):
        if self.is_locked:
            return "locked"
        if not self.script_arr:
            if self.problem_id is None:
                elog('Get Script Error', 'problem has not been loaded yet')
            if s_type not in ['cpp', 'java', 'python']:
                elog('Get Script Error', 'script type: {0} not supported'.format(s_type))
            script_text = self.parse_script(self.f_text)
            self.script_arr = json.loads(script_text)
        res = "ERROR"
        try:
            res = list(filter(lambda script: script['value'] == s_type, self.script_arr))[0]['defaultCode']
        except IndexError as err:
            elog(err, "Failed to get default code")
        return res

    def parser(self, p_type, f_text):
        match_obj = re.match(QuestionContent.reg.format(p_type), f_text, flags=re.DOTALL)
        if match_obj:
            return match_obj.group(1)
        else:
            elog("Problem Parsing Error", "Failed to parse " + p_type + " for problem: {0}".format(self.problem_id))

    def parse_content(self, f_text):
        return self.parser("CONTENT", f_text)

    def parse_script(self, f_text):
        return self.parser("SCRIPT", f_text)

    @staticmethod
    def clear_string(s):

        s = replace_newline_tab(s).replace("'", "====").replace('"', "'").replace("====", '"')[:-2] + "]"
        s = re.sub('\w+(")s', "'", s)
        match_obj = re.match('.*"(.)".*', s)
        try:
            s = re.sub('("[^Cc]{1}")', "'{0}'".format(match_obj.group(1)), s)
        except:
            print('no C default code')
        return s

    def set_content(self, content):
        # html contains escaped unicode character
        content = content.encode('utf-8').decode('unicode_escape')
        self.content = content

    """
        Usage: get script from leetcode.com and parse it to json then store to data
    """
    def set_script(self, script):
        # html contains escaped unicode character
        script = script.encode('utf-8').decode('unicode_escape')
        clear_script = self.clear_string(script)
        try:
            self.script_arr = json.loads(clear_script)
        except json.JSONDecodeError as err:
            elog(err, "error when loads json string with id: {0}".format(self.problem_id))
            with open('{0}-error.json'.format(self.problem_id), 'w') as f:
                f.write(clear_script)
            pass

    """
        Call this function when the problem is locked
    """
    def set_locked(self):
        self.is_locked = True

    def save(self):
        if self.problem_id is None:
            elog('Save Content Error', 'problem has not been loaded yet')

        if self.is_locked:
            self.f_text = "locked"
        else:
            self.f_text = ''.join(
                [
                    QuestionContent.sep.format('CONTENT', self.content),
                    QuestionContent.sep.format('SCRIPT', json.dumps(self.script_arr))
                ])

        try:
            with open(join(DATA_CONTENT_PATH, self.problem_id + ".txt"), 'w') as content:
                content.write(self.f_text)
        except IOError as err:
            elog(err, "Failed to save content with problem: {0}".format(self.problem_id))

        QuestionContent.is_loaded_table[self.problem_id] = False
        self.f_text = ""
        self.content = ""
        self.script_arr = []
        print("problem: {0} saved".format(self.problem_id), end='\r')
        self.problem_id = None

        pass
