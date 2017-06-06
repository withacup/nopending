# -*- coding: utf-8 -*-
import scrapy


class TestCaseSpiderSpider(scrapy.Spider):
    name = 'test_case_spider'
    allowed_domains = ['https://leetcode.com/accounts/login/']
    start_urls = ['http://https://leetcode.com/accounts/login//']

    def parse(self, response):
        pass
