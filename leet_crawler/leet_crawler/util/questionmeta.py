# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-12 20:28:21
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-19 15:54:05
from util.common import *
"""
    QuestionMeta manages questions_meta file
"""


class QuestionMeta:

    # This class cannot be saved when other object is loaded
    counter = 0

    def __init__(self):
        self.meta_dict = {}
        self._free_problem = []
        self._locked_problem = []

    def __iter__(self):
        for key, value in self.meta_dict.items():
            yield key, value
        
    def load(self):
        QuestionMeta.counter += 1

        self.meta_dict = JSONLoads(read_file(DATA_META_PATH, QUESTION_META_FILE))
        if not self.meta_dict:
            elog("", "failed to decode question meta json file")

        for problem_id, meta in self.meta_dict.items():
            if meta['paid_only']:
                self._locked_problem.append(problem_id)
                continue
            self._free_problem.append(problem_id)

    def get_problem(self, problem_id):
        problem_id = str(problem_id)
        if problem_id in self.meta_dict:
            return self.meta_dict[problem_id]
        return None

    def set_problem(self, problem_id, new_problem_meta):
        self.meta_dict[problem_id] = new_problem_meta

    def is_free(self, problem_id):
        if problem_id not in self.meta_dict:
            elog('Meta Error', 'Cannot find problem {0} in meta'.format(problem_id))
        return self.meta_dict[problem_id]['paid_only']

    def get_free_problem(self):
        return self._free_problem

    def get_locked_problem(self):
        return self._locked_problem

    def save(self):
        if QuestionMeta.counter > 1:
            elog('Duplicate saving Error', 'Question meta is trying to save when other qm object have not been saved')
        QuestionMeta.counter -= 1
        content = JSONDumps(self.meta_dict)
        if not content:
            elog("", "failed to dump meta dict to json file")
        write_file(content, DATA_META_PATH, QUESTION_META_FILE)
