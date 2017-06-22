# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-12 20:29:34
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-20 16:03:42
from util.common import *
from tools.syntaxparser import SyntaxParser
from tools.codegen import CodeGenerator
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
            content = JSONDumps(solution)
            if not content:
                elog('', 'failed to dump solution for problem: {0}'.format(problem_id))
            if not write_file(content, VERIFIED_SOLUTION_PATH, problem_id + '.json'):
                print("Error failed to save all verified solutions")

    @classmethod
    def save_problem(cls, problem_id):
        problem_id = str(problem_id)
        content = JSONDumps(cls.solution_table[problem_id])
        if not content:
            elog('', 'failed to dump solution for problem: {0}'.format(problem_id))
        if not write_file(content, VERIFIED_SOLUTION_PATH, problem_id + '.json'):
            print("Error failed to save problem: {0}".format(problem_id))

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
        raise NotImplementedError
        # return cls.__get_attr(problem_id, "modified_code")

    @staticmethod
    def __get_attr(problem_id, attr):
        if str(problem_id) == "127":
            print("There is a problem with 127's test case, no right solution right now")
            if attr == 'total_cases':
                return -1
            return "leetcode error"
        try:
            info = JSONLoads(read_file(VERIFIED_SOLUTION_PATH, str(problem_id) + '.json'))[attr]
            if not info:
                return None
            if type(info) is int:
                return info
            return recover_newline_tab(info)
        except KeyError as err:
            elog(err, 'Cannot get key value from verified solutions')

    @classmethod
    def is_verified(cls, problem_id):
        if cls.get_verified_code(problem_id):
            return True
        return False

    """
        Usage: analyse the default code for problem
        returns:
            array of tuples [(code, boolean describe if reach the end of test cases)]
    """
    @classmethod
    def get_modified_solution(cls, problem_ids, l_type, offset, end, boolean_value=None):
        if type(problem_ids) is not list:
            raise TypeError('problem_ids must be list instead of {0}'.format(type(problem_ids)))
        if not boolean_value:
            boolean_value = 'true'
        modified_code_result = []
        for problem_id in problem_ids:
            total_cases = cls.get_total_cases(problem_id)
            # if the number of test cases is too large, we may need to get them separately
            end = min(total_cases, end)
            # code generator, generate cases leaker
            cg = CodeGenerator(problem_id, l_type, total_cases)
            func_name = cg.get_function_names()[0]
            var = cg.generate_variable(offset=offset, end=end)
            func = cg.generate_function(boolean_value)
            # get the code that can pass all test cases, and merge case leaker into it
            v_code = cls.get_verified_code(problem_id)
            # there could be class keyword in comments, need to remove it
            v_code = remove_cjcomment(v_code)
            # prefix all entry function name with _ to avoid recursion function
            v_code = re.sub('([^a-zA-Z]){0}([^a-zA-Z])'.format(func_name), r'\1_' + func_name + r'\2', v_code)
            v_code_arr = v_code.split('\n')
            class_pos = 0
            # find class keyword and insert my case leaker
            for i in range(len(v_code_arr)):
                if 'class' in v_code_arr[i]:
                    # class_pos = i
                    line = v_code_arr[i] 
                    pos = line.find('{') + 1
                    v_code_arr[i] = line[:pos] + '\n'.join([var, func]) + line[pos:]
                    break
            # join them back
            modified_code_result.append(('\n'.join(v_code_arr), (end == total_cases)))
        return modified_code_result


        # raise NotImplementedError
    
    @classmethod
    def print_types(cls, problem_ids):
        format_str = '{problem_id:10s}{o_type:40s}{p_names:40s}{i_type:40s}{f_name}\n'
        print(format_str.format(problem_id="problem_id", i_type=str("input_type"), o_type="output_type", p_names="parameter_names", f_name="function_name"))
        for problem_id, i_type, o_type, p_names, f_name in cls.__get_iotypes(problem_ids):
            print(format_str.format(problem_id=problem_id, i_type=str(i_type), o_type=str(o_type), p_names=str(p_names), f_name=str(f_name)))

    """
        This method can analyse both cpp and java code,
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
            sp = SyntaxParser(problem_id, JAVA)
            io_types.append((problem_id, sp.get_input_type(), sp.get_output_type(), sp.get_param_name(), sp.get_func_name()))
        return io_types
