import datetime
INITIAL_RATING = 1400  # 新用户的初始 Rating
BIND_TIME_LIMIT = 120  # 绑定的时间限制(seconds)
NEW_THRESHOLD = 1000  # 'new' 的题目编号范围
DELTA = [-1400, -900, -550, -300, -150, -50]
DISPLAY_LIMIT = 20
DAILY_UPPER_BOUND = 3000
FLOWER_BIRTHDAY = datetime.datetime(2023, 3, 30)
SELF_QQ = 234465553

ELO_K = 128
"""
在（国际象棋等的）大师级比赛中，ELO Rating 的 K 值一般是 16 或 32
但是参加 duel 的都是我们代码部队的国际伟大大师或者传奇伟大大师，所以将 K 设为 128 
"""

STORAGE_PATH = 'plugins//storage//memory.pkl'
DIFF_THRESHOLD = 0.6
AVAILABLE_TAGS = ['binary search', 'bitmasks', 'brute force', 'chinese remainder theorem', 'combinatorics',
                  'constructive algorithms', 'data structures', 'dfs and similar', 'divide and conquer', 'dp', 'dsu',
                  'expression parsing', 'fft', 'flows', 'games', 'geometry', 'graph matchings', 'graphs', 'greedy',
                  'hashing', 'implementation', 'interactive', 'math', 'matrices', 'meet-in-the-middle', 'number theory',
                  'probabilities', 'schedules', 'shortest paths', 'sortings', 'string suffix structures', 'strings',
                  'ternary search', 'trees', 'two pointers', '*special problem', 'not-seen', 'new']
