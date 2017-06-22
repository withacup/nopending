# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-08 13:52:12
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-11 14:43:50
import json
import re
import time

from util.common import *
from util.data_settings import *
from util.questionsolutionservice import QuestionSolutionService
from util.questionmeta import QuestionMeta
import requests
from scrapy.selector import Selector

MAIN_URL = "https://leetcode.com"
LOGIN_URL = MAIN_URL + "/accounts/login/"
CHECK_URL = MAIN_URL + "/submissions/detail/{0}/check/"
SUBMIT_URL = MAIN_URL + "/problems/{0}/submit/"
SUBMIT_REFERER = MAIN_URL + "/problems/{0}/"
CHECK_REFERER = MAIN_URL + "/problems/{0}/"
AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"

"""

    User class is a simulator for leetcode user,
    each instance of User can login and submit solution code to any problem,
    Must login before submit

"""


class User:

    def __init__(self, account, password):
        self.account = account
        self.password = password
        self.username = None
        self.session = requests.session()
        self.qm = QuestionMeta()
        self.qm.load()
        self._accepted = []
        self._failed = []
        self._total_submission = 0

    def login(self):

        post_data = {
            "csrfmiddlewaretoken": self.__get_csrf(),
            "login": self.account,
            "password" :self.password,
        }

        post_header = {
            "Host": "leetcode.com",
            "Referer": "https://leetcode.com/",
            "User-Agent": AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": "140",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        _ = self.session.post(LOGIN_URL, data=post_data, headers=post_header)
        username = self.check_login()
        if username:
            print(username + ' logged in successfully')
            self.username = username
        else:
            elog('Login Error', 'Failed to log in as account: {0}'.format(self.account))
        pass

    """
    @usage:
        check if this user is logged in
    @return:
        if login success, return username as string
        if failed, return None
    """
    def check_login(self):
        html = self.session.get(LOGIN_URL).text
        selector = Selector(text=html)
        html_element = selector.css('#navbar-right .dropdown-toggle').extract_first()
        match_obj = None
        try:
            match_obj = re.match('.*</span>(.*)<span.*', html_element, flags=re.DOTALL)
        except TypeError as err:
            elog(err, "failed to extract user name")

        if match_obj:
            username = match_obj.group(1).strip()
            return username
        return None

    def submit_solution(self, problem_id, l_type, solution_code=None, test_mode=False, test_case=""):
        result = self.__submit_solution(problem_id, l_type, solution_code, test_mode, test_case)
        # if there is not such code in solution
        if not result:
            return None

        while 'error' in result:
            if result['error'] == "You have attempted to submit too soon. Please <a href=/subscribe/>subscribe</a> to reduce wait time.":
                time.sleep(1)
                # print('user {0} slowing'.format(self.username))
            elif result['error'] == "User is not authenticated":
                self.login()
                print('user {0} re-login'.format(self.username))
            else:
                print('unknown error: {0}'.format(result['error']))
            result = self.__submit_solution(problem_id, l_type, solution_code, test_mode, test_case)
        return result['submission_id']

    """
        @params:
            if there is not solution code provided, this function will get a solution code based on the lang_type

            solution_code: A single ascii string of solution for corresponding problem
            l_type: A single string representing the type of the solution_code
        @returns:
            None if there is no solution for this language
            the response from server if this type of solution is found
    """

    def __submit_solution(self, problem_id, l_type, solution_code=None, test_mode=False, test_case=""):
        problem_id = str(problem_id)

        if not solution_code:
            solution_arr = QuestionSolutionService.get_solution(problem_id, [l_type])
            if not solution_arr:
                print('cannot find {0} code for problem: {1}'.format(l_type, problem_id))
                return None
            solution_code, l_type = solution_arr[0]

        meta_dict = self.qm.get_problem(problem_id)
        if not meta_dict:
            elog('', 'failed to load meta data for problem: {0}'.format(problem_id))
        problem_slug = meta_dict['stat']['question__title_slug']

        # this token is not the same with the csrftmiddlewaretoken exracted from html page,
        # this one is in cookies and is not guaranteed to be unchanged after login
        X_CSRFToken = ""
        for cookie in self.session.cookies:
            if cookie.name == "csrftoken":
                X_CSRFToken = cookie.value

        submit_header = {
            "Host": "leetcode.com",
            "User-Agent": AGENT,
            "Referer": SUBMIT_REFERER.format(problem_slug),
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "X-CSRFToken": X_CSRFToken,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Length": "491",
            "Connection": "keep-alive",
        }

        post_data = {
            "question_id": problem_id,
            "data_input": test_case,
            "lang": l_type,
            "typed_code": solution_code,
            "test_mode": test_mode,
            "judge_type": "large",
        }

        response = self.session.post(SUBMIT_URL.format(problem_slug), json=post_data, headers=submit_header)
        try:
            return json.loads(response.text)
        except:
            return {'error': "User is not authenticated"}

    def analyse_submission(self, submission_id):

        result_handler = {
            10: self.__accpeted_handler,
            15: self.__runtime_error_handler,
            20: self.__compile_error_handler,
            11: self.__wrong_result_handler,
            14: self.__time_limit_exceeded_handler
        }
        result = self.__check_submission(submission_id)

        while result['state'] != 'SUCCESS':
            time.sleep(1)
            result = self.__check_submission(submission_id)

        self._total_submission += 1

        try:
            status_code = result['status_code']
        except KeyError:
            return self.__unknown_error_handler(result)

        if status_code not in result_handler:
            print("unknown status code")

        handler = result_handler[status_code]
        return handler(result)

    def get_total_accpted(self):
        return len(self._accepted)

    def get_total_failed(self):
        return len(self._failed)

    def get_accpted(self):
        return self._accepted

    def get_failed(self):
        return self._failed

    def get_total_submission(self):
        return self._total_submission

    def __accpeted_handler(self, result):
        print("user {0}'s {1} question accepted".format(self.username, result['question_id']))
        self._accepted.append(result['question_id'])
        return result, 1

    def __runtime_error_handler(self, result):
        print("user {0}'s {1} question {2}".format(self.username, result['question_id'], result['runtime_error']))
        self._failed.append(result['question_id'])
        return result, 2

    def __compile_error_handler(self, result):
        print("user {0}'s {1} question {2}".format(self.username, result['question_id'], result['compile_error']))
        self._failed.append(result['question_id'])
        return result, 3

    def __wrong_result_handler(self, result):
        print("user {0}'s {1} question wrong result".format(self.username, result['question_id']))
        self._failed.append(result['question_id'])
        return result, 4

    def __time_limit_exceeded_handler(self, result):
        print("user {0}'s {1} question time limit exceeded".format(self.username, result['question_id']))
        self._failed.append(result['question_id'])
        return result, 5

    def __unknown_error_handler(self, result):
        print("user {0}'s submission unknown error, result from server: {1}".format(self.username, result))
        if 'question_id' in result:
            self._failed.append(result['question_id'])
        return result, 6

    def __check_submission(self, submission_id):
        submission_id = str(submission_id)

        check_header = {
            "Host": "leetcode.com",
            "User-Agent": AGENT,
            "Referer": CHECK_REFERER.format(submission_id),
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
        }
        json_str = self.session.get(CHECK_URL.format(submission_id), headers=check_header).text
        res = JSONLoads(json_str)
        if not res:
            elog('', 'failed to check submission_id: {0} with response: {1}'.format(submission_id, json_str))
        return res

    def __get_csrf(self):
        reg = ".*<input type='hidden' name='csrfmiddlewaretoken' value='(.*)' />.*"
        response = self.session.get(LOGIN_URL)
        match_obj = re.match(reg, response.text.replace('\n', ' '))
        if match_obj:
            return match_obj.group(1)
        return None


def test():
    u1 = User(account='tyang8@stevens.edu', password='yangtianxiao')
    u2 = User(account='yangtianxiao123@gmail.com', password='yangtianxiao')
    u1.login()
    u2.login()
    print(u1.submit_solution(2, JAVA))
    print(u2.submit_solution(2, JAVA))
