# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-12 20:29:34
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-12 20:29:48
import re
import html  # for decode html escaped string
from util.questioncontent import QuestionContent
from util.common import *
from tools.syntaxparser import SyntaxParser

'''
solution_table = 
{
    problem_id: {
        total_cases: int,
        l_type: cs.l_type,
        verified_code: string,
        modified_code: string
    },
    ...
}
'''


class VerifiedSolutionService:

    solution_table = {}

    CPP = 'cpp'
    JAVA = 'java'
    PYTHON = 'python'

    def __init__(self):
        pass

    '''
        only call this method with clean solution code string
    '''
    @classmethod
    def load_solution_to_problem(cls, problem_id, solution_code, l_type, total_cases):

        problem_id = str(problem_id)
        l_type = str(l_type)
        total_cases = int(total_cases)

        cls.solution_table[problem_id] = {
            "solution_code": replace_newline_tab(solution_code),
            'l_type': l_type,
            'total_cases': total_cases,
            'modified_code': None
        }

    @classmethod
    def save_all(cls):
        print("saving all verified solutions... ")
        for problem_id, solution in cls.solution_table.items():
            with open(join(VERIFIED_SOLUTION_PATH, problem_id + '.json'), 'w') as f:
                f.write(json.dumps(solution))

    @classmethod
    def save_problem(cls, problem_id):
        problem_id = str(problem_id)
        with open(join(VERIFIED_SOLUTION_PATH, problem_id + '.json'), 'w') as f:
            f.write(json.dumps(cls.solution_table[problem_id]))

    """
        This method will return clean solution code
    """
    @staticmethod
    def get_verified_code(problem_id):
        try:
            with open(join(VERIFIED_SOLUTION_PATH, str(problem_id) + '.json'), 'r') as f:
                return recover_newline_tab(json.loads(f.read())['solution_code'])
        except IOError:
            return None

    @staticmethod
    def get_verified_type(problem_id):
        try:
            with open(join(VERIFIED_SOLUTION_PATH, str(problem_id) + '.json'), 'r') as f:
                return recover_newline_tab(json.loads(f.read())['l_type'])
        except IOError as err:
            return None

    @staticmethod
    def get_modified_code(problem_id):
        with open(join(VERIFIED_SOLUTION_PATH, str(problem_id) + '.json'), 'r') as f:
            return json.loads(recover_newline_tab(f.read()))['modified_code']

    @classmethod
    def is_verified(cls, problem_id):
        if cls.get_verified_code(problem_id):
            return True
        return False
    """
        Usage: analyse the defualt code for problem
    """
    @staticmethod
    def modify_solution(problem_ids):
        raise NotImplementedError
    

    @classmethod
    def print_types(cls, problem_ids):
        for problem_id, i_type, o_type in cls.__get_iotypes(problem_ids):
            print('problem: {0:3s}    {2:30s}    {1:20s}'.format(problem_id, str(i_type), str(o_type)))

    """
        return input types and output types as [[i_type, o_type], ... ]
    """
    @staticmethod
    def __get_iotypes(problem_ids):
        if type(problem_ids) is not list:
            raise TypeError('problem_ids should be a list')
        problem_ids = list(map(to_int, problem_ids))
        problem_ids = sorted(problem_ids)
        io_types = []
        for problem_id in problem_ids:
            problem_id = str(problem_id)
            qc = QuestionContent()
            qc.load(problem_id)

            # only analyse cpp code
            d_script = qc.get_script(qc.CPP)
            sp = SyntaxParser(problem_id, d_script, QuestionContent())
            io_types.append((problem_id, sp.get_input_type(), sp.get_output_type()))
        return io_types
