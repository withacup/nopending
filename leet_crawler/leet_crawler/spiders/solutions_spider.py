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

        for problem_meta in problems_metas:
            problem_id = problem_meta['stat']['question_id']
            mm.set_problem(problem_id=problem_id, new_problem_meta=problem_meta)

        for problem_id, problem in mm.meta_dict.items():
            if problem["paid_only"]:
                print("problem {0} is locked".format(problem_id))
                with open('data/questions_content/{0}.txt'.format(problem_id), 'w') as f:
                    f.write("locked")
            else:
                yield Request(url="https://leetcode.com/problems/{0}".format(problem['stat']['question__title_slug']),
                          meta={"problem_id":problem_id,},
                          callback=self.parse_problem
                          )

    def parse_problem(self, response):

        problem_id = response.meta.get('problem_id')
        problem_content = response.css('head > meta[name="description"]::attr(content)').extract_first()
        # match_obj = re.match('.*?<script>.*var pageData = (.*?)</script>.*', response.text, re.DOTALL)
        match_obj = re.match('.*codeDefinition:(.*),.*enableTestMode.*', response.text, re.DOTALL)

        if match_obj:
            problem_script = match_obj.group(1)
        else:
            print('[ERROR]: Cannot find problem script for problem' + str(problem_id))

        # html contains escaped unicode character
        # problem_content = problem_content.encode('utf-8').decode('unicode_escape')
        # self.problems[problem_id]["question-content"] = problem_content
        # problem_script = problem_script.encode('utf-8').decode('unicode_escape')
        # self.problems[problem_id]["problem_script"] = problem_script
        cm = QuestionContent()
        cm.load(problem_id, new=True)
        cm.set_content(problem_content)
        cm.set_script(problem_script)
        cm.save()

        # sep = QuestionContent.sep
        #
        # with open('data/questions_content/{0}.txt'.format(problem_id), 'w') as f:
        #         # f.write("---CONTENT_BEGIN---\n" + problem_content + "\n---CONTENT_END---\n" + "---SCRIPT_BEGIN---\n" + problem_script + "\n---SCRIPT_END---\n")
        #         f.write("".join(sep.format("CONTENT", problem_content), sep.format("SCRIPT", problem_script)))
        # print(response.text)

        pass

    def close(spider, reason):
        spider.metaManager.save()
        print('done with spider: {0}'.format(spider.name))
        # with open('data/questions_content/.json', 'w') as f:
        #     f.write(json.dumps(spider.problems))
        print('writes ok')
    # def parse(self, response):
    #
    #     response_json = json.loads(response.text)
    #     num_of_questions = len(response_json['stat_status_pairs'])
    #     print("num of questions: {0}".format(num_of_questions))
    #
    #
    #     # I use problem variable name because I'm more used to it than question
    #     # self.problems = {}
    #     # for problem_id, question in get_questions():
    #     #     self.problems[question['stat']['question_id']] = question
    #
    #     self.problems = get_questions()
    #
    #
    #     # save question information for future use
    #     with open('data/question_titles.json', 'w') as f:
    #         f.write(json.dumps(self.problems, indent=4))
    #
    #     for problem_id, problem in self.problems:
    #         yield Request(url="https://leetcode.com/problems/{0}".format(problem['stat']['question__title_slug']),
    #                       meta={"problem_id":problem_id},
    #                       callback=self.parse_problem
    #                       )
    #
    #     pass

