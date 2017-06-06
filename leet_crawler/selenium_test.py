# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-05 20:39:05
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-05 20:39:25
from selenium import webdriver
from scrapy.selector import Selector

browser = webdriver.Chrome()

browser.get("https://leetcode.com/problemset/algorithms/")

t_selector = Selector(text=browser.page_source)
t_selector.css("")
# print(browser.page_source)

browser.quit()