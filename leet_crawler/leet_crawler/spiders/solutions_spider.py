# -*- coding: utf-8 -*-
import scrapy
import json
# from util.common import get_questions
from scrapy import Request
import re
from util.Data import *

class SolutionsSpiderSpider(scrapy.Spider):
    name = 'solutions_spider'
    allowed_domains = ['leetcode.com']
    # start_urls = ['http://https://www.jiuzhang.com/solution//']
    start_urls = ['https://leetcode.com/api/problems/algorithms/']

    def start_requests(self):

        # only one manager in spider
        # self.contentManager = QuestionContent()
        self.metaManager = QuestionMeta()

        for url in self.start_urls:
            yield Request(url=url,
                callback=self.parse_meta
                )

    """
    Get questions_meta.json file from algorithms category
    """
    def parse_meta(self, response):
        
        response_dict = json.loads(response.text)
        mm = self.metaManager
        mm.load()

        problems_metas = response_dict['stat_status_pairs']

        # only update new problems
        new_problems = {}

        for problem_meta in problems_metas:
            problem_id = problem_meta['stat']['question_id']
            if str(problem_id) not in mm.meta_dict:
                new_problems[problem_id] = problem_meta
                mm.set_problem(problem_id=problem_id, new_problem_meta=problem_meta)

        for problem_id, problem in new_problems.items():
            if problem["paid_only"]:
                print("problem {0} is locked".format(problem_id))
                with open('data/questions_content/{0}.txt'.format(problem_id), 'w') as f:
                    f.write("locked")
            else:
                yield Request(
                    url="https://leetcode.com/problems/{0}".format(problem['stat']['question__title_slug']),
                    meta={"problem_id":problem_id,},
                    callback=self.parse_problem
                    )


    def parse_problem(self, response):

        solutions_url = "https://discuss.leetcode.com/api/category/{0}".format(response.css('div#tab-view-app::attr(data-notebbcid)').extract_first())

        problem_id = response.meta.get('problem_id')
        problem_content = response.css('head > meta[name="description"]::attr(content)').extract_first()
        match_obj = re.match('.*codeDefinition:(.*),.*enableTestMode.*', response.text, re.DOTALL)

        if match_obj:
            problem_script = match_obj.group(1)
        else:
            print('[ERROR]: Cannot find problem script for problem' + str(problem_id))

        cm = QuestionContent()
        cm.load(problem_id, new=True)
        cm.set_content(problem_content)
        cm.set_script(problem_script)
        cm.save()

        # TODO: for every post, get a topic requests

        yield Request(
            url=solutions_url,
            # meta={"topic_url": topic_url},
            callback=self.parse_topic
            )

        pass

    def parse_topic(self, response):
        topics = json.loads(response.text)['topics']
        for topic in topics:
            topic_url = "https://discuss.leetcode.com/api/topic/{0}".format(topic)

        pass


    def parse_solution(self, response):
        pass

    def close(spider, reason):
        spider.metaManager.save()
        print('done with spider: {0}'.format(spider.name))
        print('writes ok')











