import json
from os.path import join
from util.data_settings import *
from util.common import *
from tools.formatter import format_python
import re

from scrapy.selector import Selector # for select code part
import html # for decode html escaped string


"""
    QuestionMeta manages questoins_meta file
"""
class QuestionMeta:

    # This class cannot be re-loaded when not saved
    is_loaded = False

    def __init__(self):
        self.meta_dict = {}
        
    def load(self):
        if QuestionMeta.is_loaded:
            elog("Duplicate QuestionMeta Loading Error", "question meta is trying to load before other object save their data")
        QuestionMeta.is_loaded = True

        try:
            with open(DATA_META_PATH, 'r') as meta:
                self.meta_dict = json.loads(meta.read())
        except IOError as err:
            elog(err, "load question meta failed")

    def get_problem(self, problem_id):
        problem_id = str(problem_id)
        return self.meta_dict[problem_id]

    def set_problem(self, problem_id, new_problem_meta):
        self.meta_dict[problem_id] = new_problem_meta

    def save(self):
        QuestionMeta.is_loaded = False

        try:
            with open(DATA_META_PATH, 'w') as meta:
                meta.write(json.dumps(self.meta_dict))
        except IOError as err:
            elog(err, "save question meta failed")


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

        if self.problem_id != None:
            elog("Duplicate QuestionContent Loading Error", "question content with id: {0} is trying to load again".format(self.problem_id)) 

        if self.problem_id in QuestionContent.is_loaded_table and QuestionMeta.is_loaded_table[self.problem_id]:
            elog("Duplicate QuestionContent Loading Error", "question content is trying to load before other object save their data")

        # only read content when the problem content is not new content
        if not new:
            try:
                # this has to be str(problem_id), because self.problem_id is the identifier for this object, I have to set it at the end of the function
                with open(join(DATA_CONTENT_PATH, str(problem_id) + ".txt"), 'r') as content:
                    text = content.read()
                    if text == "locked":
                        print('problem: {0} is locked'.format(self.probelm_id))
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
            if self.problem_id == None:
                elog('Get Content Error', 'problem has not been loaded yet')
            self.content = self.parse_content(self.f_text)
        return self.content

    def get_script(self, s_type):
        if self.is_locked:
            return "locked"
        if self.script_arr == []:
            if self.problem_id == None:
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

    def clearString(self, s):

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
        clear_script = self.clearString(script)
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
        if self.problem_id == None:
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


'''
TODO:
    1. use static variable to manage all QuestionSolution objects
        , classify all solutions to their own problems
        , guarantee every problem have only one solution file
    2. analys solution syntax, get their programming language
    3. for each language in each post, only get the last <pre><code>.*</code></pre> piece of code
    3. save solutions data under question_solution directory`
'''
class QuestionSolutionService:

    # store all problems and their corresponding solutions
    problem_table = {}
    '''
    problem_table {
        problem_id:{
            qc: QuestionContent object
            posts: [
                {
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

    # lang_type | l_type
    CPP = 'cpp'
    JAVA = 'java'
    PYTHON = 'python'
    NAL = 'notalanguage'

    def __init__(self):
        pass

    @classmethod
    def load_post_to_problem(cls, problem_id, post_content_str):
        problem_id = str(problem_id)
        post_content_str = replace_newline_tab(post_content_str)

        if problem_id not in cls.problem_table:
            qc = QuestionContent()
            qc.load(problem_id)
            cls.problem_table[problem_id] = {}
            cls.problem_table[problem_id]['qc'] = qc
            cls.problem_table[problem_id]['posts'] = []

        # store three languages into the current post dict
        post = {'is_locked': False, cls.JAVA:None, cls.CPP:None, cls.PYTHON: None}

        if cls.problem_table[problem_id]['qc'].is_locked:
            post['is_locked'] = True
        else:
            code_arr = Selector(text=post_content_str).css('pre > code::text').extract()
            code_arr = list(map(html.unescape, code_arr)) # resolve html escaped charaters

            for code in code_arr:
                if cls.__verify_code(code, problem_id):
                    lang_type = cls.__analyse_lang(code)
                    code = cls.__wrap_class(code, lang_type, problem_id)
                    # format python here
                    if lang_type == QuestionSolutionService.PYTHON:
                        code = format_python(code)
                    post[lang_type] = code

        # store this post to problem table
        cls.problem_table[problem_id]['posts'].append(post)
        pass

    """
        save all posts(solutions) to data/question_solution
        should be called when there are solutions updated
    """
    @classmethod
    def save_all(cls):
        for problem_id, solution in cls.problem_table.items():
            solution['qc'] = problem_id + '.txt'
            with open(join(DATA_SOLUTION_PATH, problem_id + '.txt'), 'w') as f:
                f.write(json.dumps(solution, indent=4))
        pass

    @staticmethod
    def read_solution(problem_id, l_type):
        with open(join(DATA_SOLUTION_PATH, problem_id + '.txt'), 'r') as f:
            # [post for post in json.loads(f.read())['posts']]
            posts = json.loads(f.read())['posts']
            return [recover_newline_tab(post[l_type]) for post in posts if post[l_type]]


    # method below should not be used by outside
    @classmethod
    def __analyse_lang(cls, code):
        # TODO: analyse the language used by this code
        if 'def' in code and 'self' in code:
            return cls.PYTHON
        if 'vector' in code or 'unordered_map' in code or 'string' in code:
            return cls.CPP
        if 'ArrayList' in code or 'HashMap' in code or 'String' in code:
            return cls.JAVA
        if re.match('.*public *?[^:].*', code, flags=re.DOTALL):
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
    @staticmethod
    def __extract_func_name(code):
        # match the first function name
        match_obj = re.match('.*def (.*?)\(.*?(def|$)', code)
        if match_obj:
            return match_obj.group(1)
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
            if l_type == cls.CPP: # need to indent code
                return "class " + class_default_name + " {" + NEW_LINE + "public:" + NEW_LINE + "    " + code.replace(NEW_LINE, NEW_LINE + "    ") + NEW_LINE + "}"
            if l_type == cls.JAVA:
                return "public class " + class_default_name + " {" + NEW_LINE + "    " + code.replace(NEW_LINE, NEW_LINE + "    ") +  NEW_LINE + "}"
            # python need to be indented corrently, so I used format_python here
            return "class " + class_default_name + " :" + NEW_LINE + "    " + code.replace(NEW_LINE, NEW_LINE + "    ")
        except TypeError as err:
            elog(err, "Fuck")
            pass      


def test():
    meta = QuestionMeta()
    meta.load()
    print(meta.get_problem(111))

    content = QuestionContent()
    content.load(111)
    print(content.get_content())
    print(content.get_script(QuestionContent.PYTHON))
    print(content.get_script(QuestionContent.CPP))
    print(content.get_script(QuestionContent.JAVA))


    # cm = self.contentManager
    # cm.load(problem_id)
    # cm.set_content(problem_content)
    # cm.set_script(problem_script)
    # cm.save()
    pass














