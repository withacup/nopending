# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-08 13:52:12
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-09 16:18:56

from util.common import elog, log
from util.data_settings import *
import json
from os import path
import requests
from scrapy import Request
from scrapy.selector import Selector

try:
    import cookielib
except:
    import http.cookiejar as cookielib

import re

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename=path.join(COOKIE_PATH, "leet_login_cookies.txt"))


AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"

headers = {
    'User-Agent': AGENT
}

# get_header = {
#     "Host":"leetcode.com",
#     "Referer":"https://leetcode.com/accounts/login/",
#     "User-Agent":AGENT,
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#     "Accept-Language": "en-US,en;q=0.5",
#     "Accept-Encoding": "gzip, deflate, br",
#     "Content-Type": "application/x-www-form-urlencoded",
#     "Content-Length": "140",
#     "Connection": "keep-alive",
#     "Upgrade-Insecure-Requests": "1",
# }

post_header = {
    "Host":"leetcode.com",
    "Referer":"https://leetcode.com/",
    "User-Agent":AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-www-form-urlencoded",
    "Content-Length": "140",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

two_sum_submit_header = {
    "Host":"leetcode.com",
    "User-Agent":AGENT,
    "Referer":"https://leetcode.com/problems/two-sum/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type":"application/json",
    "X-CSRFToken":"",
    "X-Requested-With":"XMLHttpRequest",
    "Content-Length": "491",
    "Connection":"keep-alive",
}


def get_csrf():
    reg = ".*<input type='hidden' name='csrfmiddlewaretoken' value='(.*)' />.*"
    response = session.get("https://leetcode.com/accounts/login/")

    match_obj = re.match(reg, response.text.replace('\n', ' '))
    if match_obj:
        print("csrfmiddlewaretoken found: " + match_obj.group(1))
        return match_obj.group(1)
    else:
        print("failed to find csrfmiddlewaretoken")

"""
    returns: cookie_dict, response(Selector)
"""
def leet_login(account, password):
    #login
    # if re.match("1\d{10}", account):
    # print ("login with phone number")
    post_url = "https://leetcode.com/accounts/login/"
    post_data = {
        "csrfmiddlewaretoken":get_csrf(),
        "login":account,
        "password":password,
    }



    response = session.post(post_url, data=post_data, headers=post_header)
    # print(response.text)
    cookie_arr = []
    for cookie in session.cookies:
        cookie_arr.append({'name': cookie.name, 'value': cookie.value, 'path': cookie.path, 'domain': cookie.domain})
    # return session, cookie_arr, Selector(text=response.text)
    return session


def leet_request(url, callback=None, method='GET', headers=None, body=None, cookies=None, meta=None, encoding='utf-8', priority=0, dont_filter=False, errback=None, flags=None):

    headers = post_header

    return Request(url, callback, method, headers, body, cookies, meta, encoding, priority, dont_filter, errback, flags)

def get_index():
    response = session.get("https://www.leetcode.com")
    with open(path.join(DATA_TMP_PATH, "leet_index_page.html"), 'wb') as f:
        f.write(response.text.encode('utf-8'))
    # session.cookies.save()
    # print(session.cookies)
    # for cookie in session.cookies:
    #     # print (cookie.name, cookie.value, cookie.domain) #etc etc
    #     if cookies.name == "csrftoken":
    #         two_sum_submit_header
    print("ok")

def submit_twosum():
    post_url = "https://leetcode.com/problems/two-sum/submit/"
    post_data = {
        "question_id":"1",
        "data_input":"[3,2,4]6",
        "lang":"cpp",
        "typed_code":"class Solution {public:    vector<int> twoSum(vector<int>& nums, int target) {        const int len = nums.size();        for (int i = 0; i < len; i++) {            for (int j = i + 1; j < len; j++) {                if (nums[i] + nums[j] == target) {                    return {i, j};                }            }        }    }};",
        "test_mode":False,
        "judge_type":"large",
    }

    # set up header
    for cookie in session.cookies:
        if cookie.name == "csrftoken":
            two_sum_submit_header["X-CSRFToken"] = cookie.value

    # print(two_sum_submit_header)
    response = session.post(post_url, json=post_data, headers=two_sum_submit_header)

    print(json.loads(response.text))

    # with open(path.join(DATA_TMP_PATH, "two_sum_result.html"), 'wb') as f:
        # f.write(response.text.encode('utf-8'))
        # print(json.loads(response.text))
    # for cookie in session.cookies.:
    #     print(cookie)
    session.cookies.save()
    print("submit ok")

def test():
    try:
        session.cookies.load(ignore_discard=True)
    except:
        log("cookie loading failed")
    # for cookie in session.cookies:
    #     print(cookie.name, cookie.value, cookie.domain, cookie.expires, cookie.path, cookie.version, cookie.path_spec, cookie.secure)
    leet_login("tyang8@stevens.edu", "yangtianxiao")

    # get_index()
    submit_twosum()

LOGIN_URL = "https://leetcode.com/accounts/login/"
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

    def login(self):

        post_data = {
            "csrfmiddlewaretoken":self.__get_csrf(),
            "login":self.account,
            "password":self.password,
        }

        post_header = {
            "Host":"leetcode.com",
            "Referer":"https://leetcode.com/",
            "User-Agent":AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": "140",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        response = self.session.post(LOGIN_URL, data=post_data, headers=post_header)
        username = self.check_login()
        if username:
            print('logged in successfully')
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
        match_obj = re.match('.*</span>(.*)<span.*', html_element, flags=re.DOTALL)
        if match_obj:
            username = match_obj.group(1).strip()
            return username
        return None

    def __get_csrf(self):
        reg = ".*<input type='hidden' name='csrfmiddlewaretoken' value='(.*)' />.*"
        response = self.session.get(LOGIN_URL)
        match_obj = re.match(reg, response.text.replace('\n', ' '))
        if match_obj:
            return match_obj.group(1)
        return None





























