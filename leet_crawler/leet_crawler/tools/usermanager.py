# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-11 17:10:50
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-19 22:03:02
import queue, time

from util.questionsolutionservice import QuestionSolutionService as qs
from util.questionmeta import QuestionMeta as qm
from util.verifiedsolutionservice import VerifiedSolutionService as vs
from util.user import User
from concurrent.futures import ThreadPoolExecutor
from util.data_settings import *
from util.common import *

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

    def start_fetching_cases(self, problem_ids=None, l_type=JAVA):
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
                workers.append(executor.submit(self.__login_submit_modified, user=user, l_type=l_type))
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
            print('--->> number of question left: {0}'.format(self.problem_waiting_queue.qsize()))
            time.sleep(10)

    def __login_submit(self, user, priority=None):
        user.login()
        if not priority:
            priority = [JAVA, CPP, PYTHON]

        while not self.problem_waiting_queue.empty():
            start_time = time.time()

            problem_id = self.problem_waiting_queue.get()
            solutions = qs.get_solution(problem_id=problem_id, l_types=priority)

            for solution_code, l_type in solutions:
                # submit a single solution code
                submission_id = user.submit_solution(problem_id=problem_id, l_type=l_type, solution_code=solution_code)
                res, status_code = user.analyse_submission(submission_id)
                time_consumed = time.time() - start_time
                time.sleep(max(0, self._interval - time_consumed))

                if status_code == 1:
                    # if the solution code is accpeted, save the verified infomation
                    vs.load_solution_to_problem(problem_id, solution_code=solution_code, l_type=l_type, total_cases=res['total_testcases'])
                    vs.save_problem(problem_id)
                    # only verify the first submitted code
                    break

    def __login_submit_modified(self, user, l_type):
        try:

            user.login()
            while not self.problem_waiting_queue.empty():
                problem_id = self.problem_waiting_queue.get()
                # store the std_out info, in case the problem's test cases need to be get separately
                std_out_arr = self.__fetch_case(user, problem_id, l_type, MAX_TRY)
                if not std_out_arr:
                    print('failed to fetch stdout with problem: {0}'.format(problem_id))
                    continue
                content = ''.join(std_out_arr)
                write_file(content, TEST_CASES_PATH, str(problem_id) + '.txt')
                print("problem {0}'s test cases saved".format(problem_id))

        except KeyError as keyerr:
            print("Error with user: {0} err: {1}".format(user.username, keyerr))
        except IndexError as inderr:
            print("Error with user: {0} err: {1}".format(user.username, inderr))
        except IOError as ioerr:
            print("Error with user: {0} err: {1}".format(user.username, ioerr))
        except UnboundLocalError as unbounderr:
            print("Error with user: {0} err: {1}".format(user.username, unbounderr))
            # print("Error with user: {0} err: unknown error".format(user.username))

        return "User {0} submit {1} submissions, {2} accepted, {3} failed".format(user.username, str(user.get_total_submission()), str(user.get_total_accpted()), str(user.get_total_failed()))

    def __fetch_case(self, user, problem_id, l_type, max_try=10):
        # re-submit as long as it is time limit error,
        # since the solutions all verified already, so the problem will be solved eventually,
        # all cases will be cached into std_out_cache variable
        std_out_cache = []
        # some problem will need a boolean value, so there could be 50% chance for my code to fail,
        # I need to change return value dynamicly to avoid this error
        _boolean_value = 'true'
        _last_end = _last_offset = -1
        # each time a submission returns a time limit exceeded error, I need to cut the fetching length into half,
        # but when fetch succeed, I need to change fetching length back to longest length I can have.
        total_cases = vs.get_total_cases(problem_id=problem_id)
        _offset = 0
        _end = total_cases
        # only submit for max_try times
        for i in range(max_try):
            start_time = time.time()
            print("problem: {0} fetching cases: {1}-{3}/{2}".format(problem_id, _offset, total_cases, _end))
            solution_code, fetch_is_end = vs.get_modified_solution(problem_ids=[problem_id],
                                                                   l_type=l_type,
                                                                   offset= _offset,
                                                                   end=_end,
                                                                   boolean_value=_boolean_value)[0]

            # submit a single solution code
            submission_id = user.submit_solution(problem_id=problem_id,
                                                 l_type=l_type,
                                                 solution_code=solution_code)
            res, status_code = user.analyse_submission(submission_id)
            time_consumed = time.time() - start_time
            time.sleep(max(0, self._interval - time_consumed))
            _end = min(_end, total_cases)

            if _end - _offset == 0:
                print('problem: {0} test case has been tried for {1} times, ignored with fetching length {2}'.format(
                    problem_id, i, _end - _offset))
                return []
            # handle submission result
            if status_code == 5:
                # if time limit exceeded
                _end = int((_offset + _end) / 2)
                # print("problem: {0} fetched cases: {1}/{2}".format(problem_id, _offset, total_cases))


            elif status_code == 4 or status_code == 2:
                # if wrong anwser or runtime error
                std_out_cache.append(res['std_output'])
                # print("problem: {0} fetched cases: {1}/{2}".format(problem_id, _offset, total_cases))
                # if all cases are done
                if fetch_is_end:
                    return std_out_cache
                # if the fetching is not end, move the fetching query forward. In greeding approach
                # _offset, _end = _end, total_cases
                _offset, _end = _end, _end + int(1.5 * (_end - _offset))

            elif status_code == 1:
                # when the code is accepted, it's probably because its return type is boolean,
                # so assign a new boolean type may solve the problem
                # if _offset == _last_offset and _last_end == _end:
                #     print("problem: {0} is tough guy, ignoring".format(problem_id))
                #     return []
                _end = int((_offset + _end) / 2)
                _last_offset = _offset
                _last_end = _end
                if _boolean_value == 'true':
                    _boolean_value = 'false'
                else:
                    _boolean_value = 'true'
            else:
                print("user: {username}'s problem: {problem_id}'s test case fetching submission failed".format(username=user.username, problem_id=problem_id))
                return []
        print('problem: {0} test case has been tried for {1} times, ignored with fetching length {2}'.format(problem_id, max_try, _end - _offset))
        return []
