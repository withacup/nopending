# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-12 11:24:50
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-13 12:42:04
# from util.Data import  QuestionContent
import re
from util.common import *
from util.data_settings import *
from util.questioncontent import QuestionContent as qc
"""
    Parse cpp code, extract its input type and output type
"""
class SyntaxParser:
    def __init__(self, problem_id, l_type):

        self.FUNC = 'function'
        self.CLS = 'class'

        self.problem_id = problem_id
        self.qc = qc()
        self.qc.load(problem_id)
        self.encoded_code = self.qc.get_script(l_type).replace(TAB, '')
        self.func_name = self.__get_func_name(self.qc.get_script(qc.PYTHON))

    '''
        return a output TypeTree object
    '''
    def get_output_type(self):
        return self.__get_type('output')

    '''
        return a input TypeTree object
    '''
    def get_input_type(self):
        return self.__get_type('input')

    '''
        return a array of strings as parameter names
    '''
    def get_param_name(self):
        return self.__get_type('params')

    '''
        return a string representing main function's name,
            if the problem is a ood problem, it will return the class name
    '''
    def get_func_name(self):
        return self.func_name

    def __get_type(self, io_type):
        code_arr = self.encoded_code.split(NEW_LINE)
        source = ""
        for code_line in code_arr:
            if self.func_name + "(" in code_line:
                source = code_line
                break
        if not source:
            print('[ERROR]: cannot parse problem output type: {0} with its code: {1}'.format(self.problem_id, source))
        source = source.strip()

        # return output type
        # static keyword not handled(no static keyword in leetcode's defualt code)
        if io_type == "output":
            o_str_arr = source.split(self.func_name + "(")[0].strip().split()
            o_str = o_str_arr[0].strip()
            if o_str in ["public", "public:"] and len(o_str_arr) >= 2:
                o_str = o_str_arr[1].strip()
            if not o_str:
                o_str = 'void'
            type_tree = TypeTree('output<{0}>'.format(o_str))
            return type_tree

        match_obj = re.match('.*\((.*)\).*', source)

        # return input type
        if match_obj:
            i_type = match_obj.group(1)
            if not i_type:
                i_type = 'void'
            type_tree = TypeTree('input<{0}>'.format(i_type))
            if io_type == 'params':
                # return parameters' name
                return type_tree.get_param_name()
            return type_tree
        print('[ERROR]: cannot parse problem input type: {0} with its code: {1}'.format(self.problem_id, source))
        return None

    # this function is different than the function in QuestionSolution class
    def __get_func_name(self, python_code):
        return self.__get_name(python_code, self.FUNC)

    def __get_class_name(self, python_code):
        return self.__get_name(python_code, self.CLS)

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

"""
    Works both for java and cpp
"""


class TypeTree:

    def __init__(self, type_str):
        # substitute multiple spaces with one space
        type_str = re.sub(' +', ' ', type_str)
        self._p_name = []
        self._root = self.TreeNode(type_str)

    def __str__(self):
        return self.__inorder(self._root)

    def get_param_name(self):
        return self._root.get_name()

    def get_root_child(self):
        return self._root.get_child_type()

    def get_root(self):
        return self._root

    def __inorder(self, root):
        return str(self._root)

    class TreeNode():
        def __init__(self, type_str):
            type_str = type_str.strip()
            self._child = []
            self._type = type_str.split('<')[0]
            self._name = []
            # extract template params
            params_str = re.match('.*?<(.*)>.*', type_str)
            if params_str:
                self._child = [TypeTree.TreeNode(p_str) for p_str in self.__split_params(params_str.group(1))]
            # deal with java array, leetcode cpp parameter never use array
            elif type_str[len(type_str) - 1] == ']':
                self._type = '[]'
                self._child = [TypeTree.TreeNode(type_str[:-2])]


        """
            inorder traversal
        """
        def __str__(self):
            # deal with java array
            if self._type == "[]":
                if self._child:
                    return ''.join([self._child[0].__str__(), self._type])
            if self._child:
                return ''.join([self._type, '<{0}>'.format(', '.join([ch.__str__() for ch in self._child]))])
            return self. _type

        def get_type(self):
            return self._type

        def get_child_type(self):
            return self._child

        def get_name(self):
            return self._name

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

        # side effect: can modify _name variable in self
        def __strip_name(self, param_str):
            param_str = param_str.strip()
            for i in range(len(param_str) - 1, -1, -1):
                char = param_str[i]
                if char is '>':
                    return param_str
                if char is ' ':
                    self._name.append(param_str[i + 1:])
                    return param_str[:i]
                if char is '*':
                    self._name.append(param_str[i + 1:])
                    return param_str[:i + 1].replace(' ', '')
            # The string is empty
            return param_str.strip()
