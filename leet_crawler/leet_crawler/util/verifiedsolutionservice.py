# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-12 20:29:34
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-13 16:45:50
from util.common import *
from tools.syntaxparser import SyntaxParser
from tools.codegen import CodeGenerator as cg
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
    def get_total_cases(cls, problem_id):
        return cls.__get_attr(problem_id, 'total_cases')

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
    @classmethod
    def get_verified_code(cls, problem_id):
        # This is a historical problem that the verified_code is 'solution_code',
        #  I'm just too lazy to make it right
        code = cls.__get_attr(problem_id, 'solution_code')
        if not code:
            elog("Solution Error", 'No verified solution for problem: {0}'.format(problem_id))
        return code

    @classmethod
    def get_raw_verified_code(cls, problem_id):
        return replace_newline_tab(cls.get_verified_code(problem_id))

    @classmethod
    def get_verified_type(cls, problem_id):
        return cls.__get_attr(problem_id, 'l_type')

    @classmethod
    def get_modified_code(cls, problem_id):
        return cls.__get_attr(problem_id, "modified_code")

    @staticmethod
    def __get_attr(problem_id, attr):
        if str(problem_id) == "127":
            print("There is a problem with 127's test case, no right solution right now")
            if attr == 'total_cases':
                return -1
            return "leetcode error"
        try:
            with open(join(VERIFIED_SOLUTION_PATH, str(problem_id) + '.json'), 'r') as f:
                info = json.loads(f.read())[attr]
                if type(info) is int:
                    return info
                return recover_newline_tab(info)
        except IOError:
            return None
        except KeyError as err:
            elog(err, 'Cannot get key value from verified solutions')

    @classmethod
    def is_verified(cls, problem_id):
        if cls.get_verified_code(problem_id):
            return True
        return False

    """
        Usage: analyse the defualt code for problem
    """
    @classmethod
    def modify_solution(cls, problem_ids):
        if type(problem_ids) is not list:
            raise TypeError('problem_ids must be list instead of {0}'.format(type(problem_ids)))
        for _id in problem_ids:
            _cg = cg(_id, cls.JAVA)
            print(_cg.generate_variable(cls.get_total_cases(_id)))
            print(_cg.generate_function())
        # raise NotImplementedError
    
    @classmethod
    def print_types(cls, problem_ids):
        format_str = '{problem_id:10s}{o_type:40s}{p_names:40s}{i_type:40s}{f_name}\n'
        print(format_str.format(problem_id="problem_id", i_type=str("input_type"), o_type="output_type", p_names="parameter_names", f_name="function_name"))
        for problem_id, i_type, o_type, p_names, f_name in cls.__get_iotypes(problem_ids):
            print(format_str.format(problem_id=problem_id, i_type=str(i_type), o_type=str(o_type), p_names=str(p_names), f_name=str(f_name)))

    """
        This method only analyse cpp code, just because I'm more familiar with a cpp code syntax.
        return input types and output types as ((problem_id, i_type, o_type, p_name, f_name), ... )
    """
    @classmethod
    def __get_iotypes(cls, problem_ids):
        if type(problem_ids) is not list:
            raise TypeError('problem_ids should be a list')
        problem_ids = list(map(to_int, problem_ids))
        problem_ids = sorted(problem_ids)
        io_types = []
        for problem_id in problem_ids:
            problem_id = str(problem_id)
            # only analyse cpp and java code
            sp = SyntaxParser(problem_id, cls.JAVA)
            io_types.append((problem_id, sp.get_input_type(), sp.get_output_type(), sp.get_param_name(), sp.get_func_name()))
        return io_types
