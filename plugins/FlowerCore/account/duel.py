import threading, time

from . import user
from .. import crawler
import plugins.FlowerCore.account.user
from ..configs import *


def init():
    crawler.fetch_problems()


class Duel:
    def __init__(self, user1, user2, tags, index=0, not_seen=True):
        self.user1 = user1
        self.user2 = user2
        self.tags = tags
        self.index = index
        """
        tags 是一个包含了标签的数组
        第一项必然是一个 rating 数值(int)，为 800~3500 的整百数
        """
        self.status = 'pending'
        """
        pending: 等待被接受
        active: 正在进行
        finished: 已经结束
        discarded: 主动放弃
        """
        user1.duel = self
        user2.duel = self
        self.problem = None
        self.begin_time = None
        self.finish_time = None
        self.result = dict()
        self.changing = set()
        self.excluded_problems = set()
        if not_seen:
            t = threading.Thread(target=self.exclude)
            t.start()

    def duration(self):
        return self.finish_time - self.begin_time

    def rival(self, sender) -> user.User:
        if sender == self.user1:
            return self.user2
        else:
            return self.user1

    def exclude(self) -> None:
        s1, s2 = crawler.problem_record(self.user1.CF_id), crawler.problem_record(self.user2.CF_id)
        if s1 is None or s2 is None:
            return
        self.excluded_problems = s1.union(s2)
        print("exclude {:d}, {:d} => {:d} problems".format(len(s1), len(s2), len(self.excluded_problems)))

    def begin(self) -> int:
        if self.status != 'pending':
            raise Exception('The status is not "pending".')
        assert (self.user1.duel == self)
        assert (self.user2.duel == self)
        self.problem = crawler.request_problem(self.tags, self.excluded_problems)
        if self.problem is None:
            return -1  # No Such Problem
        self.status = 'active'
        self.begin_time = datetime.datetime.now()
        return 1

    def judge(self):
        if self.problem is None or self.status != 'active':
            raise Exception('The status is not "active".')
        submission1 = crawler.get_recent_submission(self.user1.CF_id)
        submission2 = crawler.get_recent_submission(self.user2.CF_id)
        if submission1 is None or submission2 is None:
            return -1  # NetWork Error
        verdict1, problem1, time1 = submission1['verdict'], submission1['problem'], \
            datetime.datetime.fromtimestamp(submission1['creationTimeSeconds'])
        verdict2, problem2, time2 = submission2['verdict'], submission2['problem'], \
            datetime.datetime.fromtimestamp(submission2['creationTimeSeconds'])
        if verdict1 == 'TESTING' or verdict2 == 'TESTING':
            return -2  # Judging
        ok1 = int(verdict1 == 'OK' and problem1 == self.problem)
        ok2 = int(verdict2 == 'OK' and problem2 == self.problem)
        if (not ok1) and (not ok2):
            return -3  # Not finished
        if [ok1 ^ 1, time1] < [ok2 ^ 1, time2]:
            self.finish(self.user1)
            return self.user1
        else:
            self.finish(self.user2)
            return self.user2

    def finish(self, winner) -> None:
        if self.status != 'active':
            raise Exception('The status is not "active".')
        assert (self.user1.duel == self)
        assert (self.user2.duel == self)
        self.finish_time = datetime.datetime.now()
        self.user1.duel = None
        self.user2.duel = None
        p = self.user1
        q = self.user2
        if winner is q:
            p, q = q, p
        self.status = 'finished'
        self.result['winner'] = winner
        self.result['old'] = [p.display_rating(), q.display_rating()]
        user.ELO.change_rating(p, q)
        self.user1.duel_history.append(self)
        self.user2.duel_history.append(self)
        self.result['new'] = [p.display_rating(), q.display_rating()]
        del self.excluded_problems

    def give_up(self, loser) -> None:
        if self.status != 'active':
            raise Exception('The status is not "active".')
        assert (self.user1.duel == self)
        assert (self.user2.duel == self)
        self.finish_time = datetime.datetime.now()
        self.user1.duel = None
        self.user2.duel = None
        self.status = 'discarded'
        self.result['loser'] = loser
        self.user1.duel_history.append(self)
        self.user2.duel_history.append(self)
        del self.excluded_problems

    def discard(self):
        if self.status != 'pending':
            raise Exception('The status is not "pending".')
        self.status = 'discarded'
        self.user1.duel = None
        self.user2.duel = None
        del self.excluded_problems

    def change(self, player) -> int:
        self.changing.add(player)
        if self.changing != {self.user1, self.user2}:
            return 0  # to be answered
        else:
            self.problem = crawler.request_problem(self.tags, self.excluded_problems)
            self.changing = set()
            return 1
