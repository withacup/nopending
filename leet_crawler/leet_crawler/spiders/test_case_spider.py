# -*- coding: utf-8 -*-
import scrapy
# from util.leet_login import leet_login, leet_request
from util.data_settings import *

from util.questionsolutionservice import QuestionSolutionService as qs
from util.questionmeta import QuestionMeta as qm
from util.verifiedsolutionservice import VerifiedSolutionService as vs
import re
from scrapy import Request
import json
import time

class TestCaseSpiderSpider(scrapy.Spider):
    name = 'test_case_spider'
    allowed_domains = ['leetcode.com']
    start_urls = ['https://leetcode.com/accounts/login//']



    def start_requests(self):
        pass
        # self.qm = qm()
        # self.qm.load()
        #
        # # login first
        # session, cookie_arr, response = leet_login(account=USER, password=PASS)
        # # print(cookie_arr)
        # # print(response.css('#navbar-right').extract())
        # html = response.css('#navbar-right .dropdown-toggle').extract_first()
        # match_obj = re.match('.*</span>(.*)<span.*', html, flags=re.DOTALL)
        # if match_obj:
        #     user_name = match_obj.group(1).strip()
        #     print('user name: {0}'.format(user_name))
        #     # yield leet_request(url='https://leetcode.com/' + user_name, callback=self.check_login, cookies=cookie_arr)
        #
        #
        #
        #     waiting_queue = list(range(700))
        #
        #     while len(waiting_queue):
        #         next_queue = []
        #         for problem_id in waiting_queue:
        #             problem_id = str(problem_id)
        #             meta = self.qm.get_problem(problem_id)
        #             if meta and not meta["paid_only"]:
        #                 code = ""
        #                 code_arr = qs.read_solution(problem_id, qs.JAVA)
        #                 if len(code_arr) > 0:
        #                     code = code_arr[0]
        #
        #                     # post here
        #
        #                     submit_headers = {}
        #                     for cookie in cookie_arr:
        #                         if cookie['name'] == "csrftoken":
        #                             submit_headers = self.get_summit_header(problem_id, cookie['value'])
        #
        #                     submit_post = self.get_submit_post(code=code, question_id=problem_id, lang=qs.JAVA)
        #                     post_url = submit_headers["Referer"] + 'submit/'
        #                     print("solving " + str(problem_id))
        #                     response = session.post(url=post_url, json=submit_post, headers=submit_headers)
        #                     print(response.text)
        #                     time.sleep(10)
        #
        #
        #     # print(response.text)
        #     # yield Request('www.leetcode.com')
        #     # yield Request(url=submit_headers["Referer"], method='POST', body=json.dumps(submit_post), headers=submit_headers, cookies=cookie_arr, callback=self.parse_submission_result, errback=self.error_handler)
        #     # body = json.dumps(submit_post)
        #     yield Request(url=post_url, method='POST', body=json.dumps(submit_post), headers=submit_headers, cookies=cookie_arr, callback=self.parse_submission_result, errback=self.error_handler)
        # else:
        #     print('log in failed')

    def error_handler(self, err):
        print(err)

    def parse(self):
        pass

    def parse_submission_result(self, response):
        print(response.text)
        pass
        # yield leet_request(url=)
        # pass

    # def check_login(self, response):
    #     username = response.css('.username::attr(title)').extract()
    #     pass

    def get_summit_header(self, problem_id, csrftoken):
        p_dict = self.qm.get_problem(problem_id)
        slug = p_dict['stat']['question__title_slug']

        submit_header = {
            "Host": "leetcode.com",
            "User-Agent": AGENT,
            "Referer": "https://leetcode.com/problems/{0}/".format(slug),
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Length": "491",
            "Connection": "keep-alive",
        }
        return submit_header
        pass

    def get_submit_post(self, code, question_id="1", data_input="[3,2,4]6", lang="cpp", test_mode=False):
        question_id = str(question_id)
        post_data = {
            "question_id": question_id,
            "data_input": data_input,
            "lang": lang,
            "typed_code": code,
            "test_mode": False,
            "judge_type": "large",
        }
        return post_data

    # def get_submit_code(self, problem_id, l_type):
