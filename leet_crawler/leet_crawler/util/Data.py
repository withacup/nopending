import json
from os.path import join
from util.data_settings import *
from util.common import log as mylog, elog
import re

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
        self.problem_id = None

    def load(self, problem_id, new=True):

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
                        log('problem: {0} is locked'.format(self.probelm_id))
                    self.f_text = text
            except IOError as err:
                elog(err, "load question: {0} content failed".format(self.problem_id))

        self.problem_id = str(problem_id)
        QuestionContent.is_loaded_table[self.problem_id] = True

    def get_content(self):
        if self.content == "":
            if self.problem_id == None:
                elog('Get Content Error', 'problem has not been loaded yet')
            self.content = self.parse_content(self.f_text)
        return self.content

    def get_script(self, s_type):
        if self.script_arr == []:
            if self.problem_id == None:
                elog('Get Script Error', 'problem has not been loaded yet')
            if s_type not in ['cpp', 'java', 'python']:
                elog('Get Script Error', 'script type: {0} not supported'.format(s_type))
            script_text = self.parse_script(self.f_text)
            self.script_arr = json.loads(script_text)

        return list(filter(lambda script: script['value'] == s_type, self.script_arr))[0]['defaultCode']

    def parser(self, p_type, f_text):
        match_obj = re.match(QuestionContent.reg.format(p_type), f_text, flags=re.DOTALL)
        if match_obj:
            return match_obj.group(1)
        else:
            elog("Problem Parsing Error", "Failed to parse " + p_type + " for problem: {0}".format(self.problem_id))

    def parse_content(self, f_text):
        self.parser("CONTENT", f_text)

    def parse_script(self, f_text):
        self.parser("SCRIPT", f_text)

    def clearString(self, s):
        s = s.replace('\r\n', ' ').replace('\n', ' ').replace('\t', '    ').replace("'", "====").replace('"', "'").replace("====", '"')[:-2] + "]"
        s = re.sub('\w+(")s', "'", s)
        match_obj = re.match('.*"(.)".*', s)
        s = re.sub('("[^Cc]{1}")', "'{0}'".format(match_obj.group(1)), s)
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
            print("error when loads json string with id: {0}".format(self.problem_id))
            with open('{0}-error.json'.format(self.problem_id), 'w') as f:
                f.write(clear_script)
            pass

    def save(self):
        if self.problem_id == None:
            elog('Save Content Error', 'problem has not been loaded yet')

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














