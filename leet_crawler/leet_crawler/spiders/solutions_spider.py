# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from util.Data import *
from util.data_settings import *

class SolutionsSpiderSpider(scrapy.Spider):
    name = 'solutions_spider'
    allowed_domains = ['leetcode.com']
    start_urls = ['https://leetcode.com/api/problems/algorithms/']

    def start_requests(self):

        # only one manager in spider
        self.qm = QuestionMeta()
        self.qservice = QuestionSolutionService()

        for url in self.start_urls:
            yield Request(url=url,
                callback=self.parse_meta
                        )

    """
    Get questions_meta.json file from algorithms category
    """
    def parse_meta(self, response):
        
        response_dict = json.loads(response.text)
        qm = self.qm
        qm.load()

        problems_metas = response_dict['stat_status_pairs']

        # only update new problems
        new_problems = {}

        for problem_meta in problems_metas:
            problem_id = problem_meta['stat']['question_id']
            if str(problem_id) not in qm.meta_dict:
                new_problems[problem_id] = problem_meta
                qm.set_problem(problem_id=problem_id, new_problem_meta=problem_meta)

        for problem_id, problem in new_problems.items():
            if problem["paid_only"]:
                print("problem {0} is locked".format(problem_id))
                cm = QuestionContent()
                cm.load(problem_id, new=True)
                cm.set_locked()
                cm.save()
            else:
                # problems/{int problem_id} -> api/category/{int solution_num} -> api/topic/{int topic_id}/{str simplified-topic-title} 
                # the post is in response[posts][0]
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

        yield Request(
            url=solutions_url,
            meta={"problem_id":problem_id,},
            callback=self.parse_topic
            )

    def parse_topic(self, response):
        problem_id = response.meta.get('problem_id')
        topics = json.loads(response.text)['topics']
        # find 5 highest voted topics on this problem
        if len(topics) > MAX_TOPIC:
            topics = topics[:MAX_TOPIC]

        for topic_id, topic in enumerate(topics):
            topic_url = "https://discuss.leetcode.com/api/topic/{0}".format(topic['slug'])
            yield Request(
                url=topic_url,
                meta={"problem_id":problem_id, 'topic_id': topic_id},
                callback=self.parse_solution
                )

    def parse_solution(self, response):
        problem_id = response.meta.get('problem_id')
        topic_id = response.meta.get('topic_id')
        res_dict = json.loads(response.text)

        content = res_dict['posts'][0]['content']
        post_title = res_dict['title']

        self.qservice.load_post_to_problem(problem_id=problem_id,
                                           post_content_str=content,
                                           topic_id=topic_id,
                                           max_topic=MAX_TOPIC,
                                           topic_title=post_title)

    def close(spider, reason):
        if not DEBUG:
            spider.qm.save()
        print('saving solutions...')
        spider.qservice.save_all()
        print('done with spider: {0}'.format(spider.name))
        print('writes ok')











