from ..configs import *


class User:
    def __init__(self, qq):
        """
        :param qq: 用户的 qq 号，以 int 形式存储
        """
        self.qq = qq
        self.duel_history = []
        self.badge = []
        self.rating = INITIAL_RATING
        self.duel = None
        self.CF_id = None
        self.bind = None
        self.daily_passed = []
        self.daily_score = 0

    def display_rating(self):
        cnt = len([x for x in self.duel_history if x.status == 'finished'])
        if cnt >= len(DELTA):
            return self.rating
        return self.rating + DELTA[cnt]

    def name(self):  # 用户的显示名称
        base_name = str(self.qq)
        if self.CF_id is not None:
            base_name = self.CF_id
        for x in self.badge:
            base_name += x
        return base_name


class ELO:
    @classmethod
    def expected(cls, Ra, Rb):
        return 1.0 / (1 + 10 ** ((Rb - Ra) / 400.0))

    @classmethod
    def new(cls, Ra, Rb, res):
        det = int(ELO_K * (res - cls.expected(Ra, Rb)))
        Ra1 = Ra + det
        Rb1 = Rb - det
        return Ra1, Rb1

    @classmethod
    def change_rating(cls, winner, loser):
        d1, d2 = cls.new(winner.rating, loser.rating, 1)
        winner.rating = d1
        loser.rating = d2
