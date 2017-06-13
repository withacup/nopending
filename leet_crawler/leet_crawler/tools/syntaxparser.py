# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-12 11:24:50
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-12 11:50:19
# from util.Data import  QuestionContent
import re
from util.common import *
from util.data_settings import *

"""
    Parse cpp code, extract its input type and output type
"""
class SyntaxParser:
    def __init__(self, problem_id, encoded_code, qc):

        self.FUNC = 'function'
        self.CLS = 'class'

        self.problem_id = problem_id
        self.encoded_code = encoded_code.replace(TAB, '')
        qc.load(problem_id)
        python_code = qc.get_script(qc.PYTHON)
        self.func_name = self.__get_func_name(python_code)


    def get_output_type(self):
        return self.__get_type('output')

    def get_input_type(self):
        return self.__get_type('input')

    def __get_type(self, type):
        code_arr = self.encoded_code.split(NEW_LINE)
        source = ""
        for code_line in code_arr:
            if self.func_name + "(" in code_line:
                source = code_line
                break
        if not source:
            print('cannot parse problem output type: {0} with its code: {1}'.format(self.problem_id, source))

        # return output type
        source = source.strip()
        if type == "output":
            o_str = source.split(self.func_name + "(")[0].strip()
            if not o_str:
                o_str = 'void'
            type_tree = TypeTree('output<{0}>'.format(o_str))
            return str(type_tree)

        # return input type
        match_obj = re.match('.*\((.*)\).*', source)
        if match_obj:
            i_type = match_obj.group(1)
            if not i_type:
                i_type = 'void'
            type_tree = TypeTree('input<{0}>'.format(i_type))
            return str(type_tree)
        print('[ERROR]: cannot parse problem input type: {0} with its code: {1}'.format(self.problem_id, source))
        return None

    # this function is different than the function in QuestionSolution class
    def __get_func_name(self, python_code):
        return self.__get_name(python_code, self.FUNC)
        # the reg below is matching the first function name in python_code
        # py_lines = python_code.split(NEW_LINE)
        # for py_line in py_lines:
        #     match_obj = re.match('.*?def (.*?)\(.*?(def|$)', py_line)
        #     if match_obj:
        #         name = match_obj.group(1)
        #         if name == '__init__':
        #             return self.__get_class_name(python_code)
        #         return match_obj.group(1)
        # elog("Data error", "Cannot extract function name from code: {0}".format(python_code))

    def __get_class_name(self, python_code):
        return self.__get_name(python_code, self.CLS)
        # for line in python_code.split(NEW_LINE):
        #     line = line.strip()
        #     if line and line[0] != '#':
        #         match_obj = re.match('^class (.*?)[(|:].*', line, flags=re.DOTALL)
        #         if match_obj:
        #             return match_obj.group(1)
        # elog("Data error", "Connot extract class name from code: {0}".format(python_code))

    def __get_name(self, python_code, n_type):
        reg = '.*?def (.*?)\(.*?(def|$)'
        if n_type is self.CLS:
            reg = '^class (.*?)[(|:].*'
        for line in python_code.split(NEW_LINE):
            line = line.strip()
            if line and line[0] != '#':
                match_obj = re.match(reg, line, flags=re.DOTALL)
                if match_obj:
                    name = match_obj.group(1)
                    if n_type is self.FUNC and name == '__init__':
                        return self.__get_name(python_code, self.CLS)
                    return match_obj.group(1)
        elog("Data error", "Cannot extract {1} name from code: {0}".format(python_code, type))


class TypeTree:

    def __init__(self, type_str):
        # substitute multiple spaces with one space
        type_str = re.sub(' +', ' ', type_str)
        self._root = self.TreeNode(type_str)

    def __str__(self):
        return self.__inorder(self._root)

    def __inorder(self, root):
        _type = root.get_type()
        _child = root.get_child_type()
        if _child:
            return ''.join([_type, '<{0}>'.format(', '.join([self.__inorder(ch) for ch in _child]))])
        return _type

    class TreeNode:
        def __init__(self, type_str):
            type_str = type_str.strip()
            self._child = []
            self._type = type_str.split('<')[0]
            # extract template params
            params_str = re.match('.*?<(.*)>.*', type_str)
            if params_str:
                self._child = [TypeTree.TreeNode(p_str) for p_str in self.__split_params(params_str.group(1))]

        def get_type(self):
            return self._type

        def get_child_type(self):
            return self._child

        def __split_params(self, params_str):
            angles = left = 0
            type_str_arr = []
            end = 0
            for i, char in enumerate(params_str):
                if char is ',' and angles is 0:
                    type_str_arr.append(self.__strip_name(params_str[left:i]))
                    left = i + 1
                if char is '<':
                    angles += 1
                if char is '>':
                    angles -= 1
                end = i
            type_str_arr.append(self.__strip_name(params_str[left:end + 1]))
            return type_str_arr

        def __strip_name(self, param_str):
            param_str = param_str.strip()
            for i in range(len(param_str) - 1, -1, -1):
                char = param_str[i]
                if char is '>':
                    return param_str
                if char is ' ':
                    return param_str[:i]
                if char is '*':
                    return param_str[:i + 1].replace(' ', '')
            return param_str
