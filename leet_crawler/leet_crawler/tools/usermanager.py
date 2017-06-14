# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-11 17:10:50
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-11 19:19:31
import queue, time

from util.questionsolutionservice import QuestionSolutionService as qs
from util.questionmeta import QuestionMeta as qm
from util.verifiedsolutionservice import VerifiedSolutionService as vs
from util.leet_login import User
from concurrent.futures import ThreadPoolExecutor

class UserManager:
    """
    @params:
        accounts: A two-dimentional array. [[account, password]]
    """
    def __init__(self, accounts):
        self.qm = qm()
        self.qm.load()
        self.problem_waiting_queue = queue.Queue()
        self.users = [User(account=account[0], password=account[1]) for account in accounts]
        self._interval = 11

    """
        Verify the solutions crawled from leetcode,
        @params:
            problem_ids: list of strings representing the problems to be verified, 
                if this value is None, then all free solutions will be verified
    """
    def start_verify_solution(self, problem_ids=None, solution_code=None, priority=None):
        users = self.users

        if problem_ids and type(problem_ids) is not list:
            raise TypeError('problem_ids should be list of strings')
        if not problem_ids:
            problem_ids = self.qm.get_free_problem()
        for problem_id in problem_ids:
            self.problem_waiting_queue.put(problem_id)

        # one more thread for timer
        with ThreadPoolExecutor(len(users) + 1) as executor:
            workers = []
            for user in users:
                workers.append(executor.submit(self.__login_submit, user=user, priority=priority))
            executor.submit(self.__print_problem_left)

            for worker in workers:
                print(worker.result())

    # get all unverified problem's ids and return as a list of strings
    def get_all_unverified_problem(self, qm, vs):
        return [ problem_id for problem_id, meta in qm if not vs.is_verified(problem_id) ]

    # get all unverified problem's code types and return as a list of strings
    def get_all_verified_code_type(self, qm, vs, problem_ids=None):
        return [ vs.get_verified_type(problem_id) for problem_id in qm ]

    # qsize function is not accurate, it only returns a approximately size of the waiting queue
    def __print_problem_left(self):
        while not self.problem_waiting_queue.empty():
            time.sleep(10)
            print('--->> number of question left: {0}'.format(self.problem_waiting_queue.qsize()))

    def __login_submit(self, user, priority=None):
        user.login()
        if not priority:
            priority = [qs.JAVA, qs.JAVA, qs.PYTHON]

        while not self.problem_waiting_queue.empty():
            start_time = time.time()

            problem_id = self.problem_waiting_queue.get()
            solutions = qs.read_solution(problem_id=problem_id, l_types=priority)

            for solution_code, l_type in solutions:
                # submit a single solution code 
                submission_id = user.submit_solution(problem_id=problem_id, l_type=l_type, solution_code=solution_code)
                res, status_code = user.analyse_submission(submission_id)
                time_consumed = time.time() - start_time
                if time_consumed < self._interval:
                    time.sleep(self._interval - time_consumed)

                if status_code == 1:
                    # if the solution code is accpeted, save the verified infomation
                    vs.load_solution_to_problem(problem_id, solution_code=solution_code, l_type=l_type, total_cases=res['total_testcases'])
                    vs.save_problem(problem_id)
                    # only verify the first submitted code
                    break

        return "User {0} submit {1} submissions, {2} accepted, {3} failed".format(user.username, str(user.get_total_submission()), str(user.get_total_accpted()), str(user.get_total_failed()))
