from .. import crawler
from ..configs import *


class CFBindAction:
    def __init__(self, user, CF_id):
        """
        :param user:  执行这一绑定的用户
        :param CF_id: 正在绑定的 CF 账号
        """
        self.user = user
        self.CF_id = CF_id
        self.begin_time = datetime.datetime.now()

    def finish(self) -> None:
        self.user.CF_id = self.CF_id

    def check(self) -> int:
        submission = crawler.get_recent_submission(self.CF_id)
        if submission is None:
            return -3  # 网络错误
        verdict, problem, time = submission['verdict'], submission['problem'], \
            datetime.datetime.fromtimestamp(submission['creationTimeSeconds'])
        if time < self.begin_time or time > self.begin_time + datetime.timedelta(seconds=BIND_TIME_LIMIT):
            return -1  # 没有按时提交
        if verdict == 'COMPILATION_ERROR' and crawler.problem_name(problem) == '1A':
            self.finish()
            return 1
        return -2
