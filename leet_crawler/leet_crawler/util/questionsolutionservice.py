# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-12 20:29:03
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-12 20:30:10
import re
import html  # for decode html escaped string

from util.common import *
from tools.formatter import format_python
from scrapy.selector import Selector  # for select code part
from util.questioncontent import QuestionContent
'''
Usage:
    There is hundreds of solutions files in data directory,
    I don't want to load them all into memory, so I make this question solution class
    a service class, every function in it is static function or class function
Description:
    1. use static variable to manage all QuestionSolution objects
        , classify all solutions to their own problems
        , guarantee every problem have only one solution file
    2. analys solution syntax, get their programming language
    3. for each language in each post, only get the last <pre><code>.*</code></pre> piece of code
    3. save solutions data under question_solution directory`
    
problem_table {
    problem_id:{
        qc: QuestionContent object
        posts: [
            {
                topic_title: string
                is_locked: bool
                cpp: string | none
                java: string | none
                python: string | none
            },
            ...
        ]
    },
    ...
}
'''


class QuestionSolutionService:

    # store all problems and their corresponding solutions
    problem_table = {}

    # lang_type | l_type
    CPP = 'cpp'
    JAVA = 'java'
    PYTHON = 'python'
    NAL = 'notalanguage'

    def __init__(self):
        pass

    @classmethod
    def load_post_to_problem(cls, problem_id, post_content_str, topic_title, topic_id, max_topic=MAX_TOPIC):
        problem_id = str(problem_id)
        post_content_str = replace_newline_tab(post_content_str)

        if problem_id not in cls.problem_table:
            qc = QuestionContent()
            qc.load(problem_id)
            cls.problem_table[problem_id] = {}
            cls.problem_table[problem_id]['qc'] = qc
            cls.problem_table[problem_id]['posts'] = [{}]*max_topic

        # store three languages into the current post dict
        post = {'is_locked': False,
                cls.JAVA: None,
                cls.CPP: None,
                cls.PYTHON: None,
                'topic_title': topic_title}

        if cls.problem_table[problem_id]['qc'].is_locked:
            post['is_locked'] = True
        else:
            code_arr = Selector(text=post_content_str).css('pre > code::text').extract()
            code_arr = list(map(html.unescape, code_arr))   # resolve html escaped characters

            for code in code_arr:
                if cls.__verify_code(code, problem_id):
                    lang_type = cls.__analyse_lang(code)
                    code = cls.__wrap_class(code, lang_type, problem_id)
                    # format python here
                    if lang_type == QuestionSolutionService.PYTHON:
                        code = format_python(code)
                    post[lang_type] = code

        # store this post to problem table
        cls.problem_table[problem_id]['posts'][topic_id] = post
        pass

    """
        save all posts(solutions) to data/question_solution
        should be called when there are solutions updated
    """
    @classmethod
    def save_all(cls):
        for problem_id, solution in cls.problem_table.items():
            solution['qc'] = problem_id + '.json'
            with open(join(DATA_SOLUTION_PATH, problem_id + '.json'), 'w') as f:
                f.write(json.dumps(solution, indent=4))
        pass

    """
        return: 
            A two-imensional array [ [ solution_code, l_type ], ... ]
    """
    @staticmethod
    def read_solution(problem_id, l_types):
        problem_id = str(problem_id)
        if type(l_types) is not list:
            raise TypeError("l_types should be a list")

        solutions = []
        with open(join(DATA_SOLUTION_PATH, problem_id + '.json'), 'r') as f:
            posts = json.loads(f.read())['posts']
            for l_type in l_types:
                solutions.extend([[recover_newline_tab(post[l_type]), l_type] for post in posts if l_type in post and post[l_type]])
        return solutions

    # method below should not be used by outside
    @classmethod
    def __analyse_lang(cls, code):
        if re.match('.*public *?[^:].*', code, flags=re.DOTALL):
            return cls.JAVA
        # spilt the code into word, in case their are something like lengthOfLongestSubstring
        # and remove all empty strings
        code = list(filter(lambda s: s and s != "newline" and s != 'tab', re.split('[^a-zA-Z]', code)))
        if 'def' in code and 'self' in code:
            return cls.PYTHON
        if 'vector' in code or 'unordered_map' in code or 'string' in code:
            return cls.CPP
        if 'ArrayList' in code or 'HashMap' in code or 'String' in code:
            return cls.JAVA
        return cls.CPP

    @classmethod
    def __verify_code(cls, code, problem_id):

        qc = cls.problem_table[problem_id]['qc']

        default_python = qc.get_script(cls.PYTHON)
        default_cpp = qc.get_script(cls.CPP)
        # extract function name for this language
        func_name_default = cls.__extract_func_name(default_python)
        # remove comments and spaces in cpp and java
        default_cpp = ' '.join(re.sub('//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"', '', default_cpp, flags=re.DOTALL).split())

        # remove comments in python (don't know how to write the regular expression)
        # default_code = re.sub('.*(""".*?""").*', '', default_code)

        if func_name_default not in code or len(code) < len(default_cpp):
            return False
        return True

    """
        only work for python default script
        (because python is easier to analyse lol)
    """
    @classmethod
    def __extract_func_name(cls, code):
        # match the first function name
        # the reg below is matching the last function name in default code
        match_obj = re.match('.*def (.*?)\(.*?(def|$)', code)
        if match_obj:
            return match_obj.group(1)
            # if name == '__init__':
            #     return cls.__extract_class_name(code)
            # return name
        else:
            elog("Data error", "Cannot extract function name from code: {0}".format(code))

    @staticmethod
    def __extract_class_name(code):
        # remove comments
        # code = re.sub('//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"', '', code)
        for line in code.split(NEW_LINE):
            if line and line[0] != '#':
                match_obj = re.match('^class (.*?)[(|:].*', line, flags=re.DOTALL)
                if match_obj:
                    return match_obj.group(1)
        elog("Data error", "Connot extract class name from code: {0}".format(code))

    @classmethod
    def __wrap_class(cls, code, l_type, problem_id):

        qc = cls.problem_table[problem_id]['qc']

        python_script = qc.get_script(cls.PYTHON)

        class_default_name = cls.__extract_class_name(python_script)
        try:
            if 'class' in code:
                return code
            if l_type == cls.CPP:  # need to indent code
                return "class " + class_default_name + " {" + NEW_LINE + "public:" + NEW_LINE + "    " + code.replace(NEW_LINE, NEW_LINE + "    ") + NEW_LINE + "};"
            if l_type == cls.JAVA:
                return "public class " + class_default_name + " {" + NEW_LINE + "    " + code.replace(NEW_LINE, NEW_LINE + "    ") +  NEW_LINE + "}"
            # python need to be indented corrently, so I used format_python here
            return "class " + class_default_name + " :" + NEW_LINE + "    " + code.replace(NEW_LINE, NEW_LINE + "    ")
        except TypeError as err:
            elog(err, "Fuck")
            pass      
