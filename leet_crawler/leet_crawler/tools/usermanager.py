# -*- coding: utf-8 -*-
# @Author: Tianxiao Yang
# @Date:   2017-06-11 17:10:50
# @Last Modified by:   Tianxiao Yang
# @Last Modified time: 2017-06-16 17:14:25
import queue, time

from util.questionsolutionservice import QuestionSolutionService as qs
from util.questionmeta import QuestionMeta as qm
from util.verifiedsolutionservice import VerifiedSolutionService as vs
from util.leet_login import User
from concurrent.futures import ThreadPoolExecutor
from util.data_settings import *

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

    def start_verify_modified_solution(self, problem_ids=None, l_type=vs.JAVA):
        try:
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
        except KeyError as err:
            print()

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
                _offset = 0
                _end = vs.get_total_cases(problem_id=problem_id)

                # store the std_out info, in case the problem's test cases need to be get separately
                std_out_arr = self.__fetch_case(user, problem_id, _offset, _end, l_type, 30)

                if std_out_arr:
                    with open(join(TEST_CASES_PATH, ".".join([str(problem_id),'txt'])), 'w') as f:
                        f.write(''.join(std_out_arr))
                    print("problem {0}'s test cases saved".format(problem_id))
        except KeyError as keyerr:
            print("Error with user: {0} err: {1}".format(user.username, keyerr))
        except IndexError as inderr:
            print("Error with user: {0} err: {1}".format(user.username, inderr))
        except IOError as ioerr:
            print("Error with user: {0} err: {1}".format(user.username, ioerr))
        except:
            print("Error with user: {0} err: unknown error".format(user.username))





        return "User {0} submit {1} submissions, {2} accepted, {3} failed".format(user.username, str(user.get_total_submission()), str(user.get_total_accpted()), str(user.get_total_failed()))

    def __fetch_case(self, user, problem_id, _offset, _end, l_type, max_try=None):
        # re-submit as long as it is time limit error, 
        # since the solutions all verified already, so the problem will be solved eventually
        std_out_cache = []
        _boolean_value = 'true'
        total_cases = _end
        for i in range(max_try):
            start_time = time.time()
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

            if status_code == 5:
                # if time limit exceeded
                _end = int((_offset + _end) / 2)
                if _end - _offset == 0:
                    print('problem: {0} test case has been tried for {1} times, ignored with fetching length {2}'.format(problem_id, i, _end - _offset))
                    return []
            elif status_code == 4 or status_code == 2:
                std_out_cache.append(res['std_output'])
                # if all cases are done
                if fetch_is_end:
                    return std_out_cache
                # if the fetching is not end, move the fetching query forward. In greeding approach
                # _offset, _end = _end, 2 * _end - _offset
                _offset, _end = _end, total_cases
            # when the code is accepted, it's probably because its return type is boolean,
            # so assign a new boolean type may solve the problem
            elif status_code == 1 and _boolean_value == 'true':
                _boolean_value = 'false'
            else:
                print("user: {username}'s problem: {problem_id}'s test case fetching submission failed".format(username=user.username, problem_id=problem_id))
                return []
        print('problem: {0} test case has been tried for {1} times, ignored with fetching length {2}'.format(problem_id, max_try, _end - _offset))
        return []
