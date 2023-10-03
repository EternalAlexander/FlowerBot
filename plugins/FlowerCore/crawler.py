import random
import time
import requests
from plugins.FlowerCore.configs import *


def link(problem):
    try:
        return "https://codeforces.com/problemset/problem/" + str(problem['contestId']) + '/' + str(
            problem['index'])
    except KeyError:
        return str(problem)


def get_recent_submission(CF_id):
    try:
        json = requests.get('https://codeforces.com/api/user.status?handle={:s}&from=1&count=1'.format(CF_id)).json()
        print(json)
        if json['status'] == 'FAILED':
            return None
        try:
            return json['result'][0]
        except IndexError:
            return None
    except requests.exceptions.JSONDecodeError:
        return None


def problem_name(problem, rating=False):
    try:
        if rating:
            return str(problem['contestId']) + str(problem['index']) + '(*{:d})'.format(problem['rating'])
        return str(problem['contestId']) + str(problem['index'])
    except KeyError:
        return str(problem)


problems = []


def fetch_problems() -> bool:
    global problems
    for cnt in range(10):
        try:
            problems = (requests.get('https://codeforces.com/api/problemset.problems').json())['result']['problems']
            return True
        except BaseException:
            pass
    return False


def daily_problem():
    t = time.localtime(time.time())
    res = []
    for x in problems:
        try:
            if x['rating'] <= DAILY_UPPER_BOUND:
                res.append(x)
        except KeyError:
            pass
    seed = (t.tm_year * 10000 + t.tm_mon * 33 * t.tm_mday) % len(res)
    return res[seed]


def problem_record(user):
    try:
        try:
            d = requests.get('https://codeforces.com/api/user.status?handle=' + user, timeout=5)
        except TimeoutError:
            return set()
        JSON = d.json()
        if JSON['status'] != 'OK':
            return []
        res = {problem_name(x["problem"]) for x in JSON['result']}
        return res
    except:
        return set()


def request_problem(tags, excluded_problems=None):
    if excluded_problems is None:
        excluded_problems = set()
    assert (type(tags[0]) == int)
    rating = tags[0]
    tags = tags[1:]
    result = []
    for x in problems:
        if (not 'tags' in x) or (not 'rating' in x) or (not 'contestId' in x):
            continue
        if excluded_problems is not None:
            if problem_name(x) in excluded_problems:
                continue
        flag = 1
        for y in tags:
            if y == 'not-seen':
                continue
            if y[0] != '!':
                if y == 'new':
                    if 'contestId' in x and x['contestId'] < NEW_THRESHOLD:
                        flag = 0
                    continue
                if not y in x['tags']:
                    flag = 0
            else:
                if y == '!new':
                    if 'contestId' in x and x['contestId'] >= NEW_THRESHOLD:
                        flag = 0
                    continue
                if y[1:] in x['tags']:
                    flag = 0
        if not flag:
            continue
        if x['rating'] == rating:
            result.append(x)
    if not result:
        return None
    return random.choice(result)
