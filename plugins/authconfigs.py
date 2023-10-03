from filemanage import *
import os

self_QQ = '234465553'
super_admin = '2496097294'

blacklist = syncfrom('blacklist.json', [])
admin_QQ = syncfrom('admin.json', ['2496097294'])
groupauth = syncfrom('groupauth.json', {})

MAINPATH = 'C:\\Users\Administrator\Downloads\\flowerbot'
try:
    os.listdir(MAINPATH)
except:
    MAINPATH = 'C:\\Users\Luhao Yan\Desktop\工程\Mirai\\alicebot-starter\\'

permanent = ['manage']

plugin_data = {
    'manage': '''/manage enable|disable [模块名称]：在当前群组开启/关闭模块
/manage blacklist add|remove @user：将用户 user 加入/移出黑名单
/manage admin add|remove @user：将用户 user 加入/移出管理''',
    'hello': """/hello ： 向 flower 打招呼
/help ： 查询帮助
/news 检查上一次的更新讯息
/heartbeat：检查 bot 是否存活
/test：检查向 CF/AT 的连接
/exec [指令]：执行这段指令""",
    'bind': """/bind begin Codeforces用户名 绑定你的 CF 账号""",
    'wordle': '''/wordle 用法：
/wordle new x 开始新游戏，单词长度为 x
/wordle guess [单词] 猜测单词
/wordle remain 查看剩下的字母
/wordle giveup 放弃当前游戏''',
    'duel': '''/duel 用法：
/duel challenge @p rating：挑战用户p，题目将随机选取一道分数为 rating 的题目
/duel ongoing: 查询正在进行的单挑
/duel query @p：查询用户 p 的 ELO rating
/duel ranklist: 查询排行榜
/duel history @p 查询用户 p 的单挑历史
/duel statics: 查询历史统计
/duel problem rating：随机一道分数为 rating 的题目''',
    'competition': '''/competition 用法：
/competition register：注册比赛
/competition quit：取消注册
/competition list：查询当前选手列表
/competiton rules：查询比赛规则'''
}

manuel = {
    'duel': ["""在使用 /duel 进行单挑之前，请先使用 /bind 绑定自己的 CF 账号""",
             """/duel challenge @p rating [tags]：挑战用户p，题目将随机选取一道分数为 rating，标签为 [tags] 的题目
             
标签的用法为：输入 CF 题目中包含的标签，多个标签用空格隔开，本身包含空格的标签请将空格用下划线 "_" 替换。可以在标签前加上 "!" ，表示要求不包含该标签。

例如：
/duel challenge @EternalAlexander 2400 geometry !data_structures
输入以上指令，将挑战用户 EternalAlexander，题目将随机选取一道 rating 为 2400，标签包含 geometry，且不包含 data structures 的题目。

另外支持两个 CF 中不包含的标签。new 将筛选比赛 id >= 1000 的题目，not-seen 将筛选自己没有提交过的题目。""",
             """/duel problem rating [tags]：随机一道分数为 rating ，标签为 [tags] 的题目。tag 的用法和 /duel challenge 中一致
""",
             """/duel daily problem 访问今天的每日挑战题目
通过每日挑战题目可以得到相应的积分
/duel daily ranklist 可以查询总积分排行""",
             """/duel ongoing: 查询正在进行的单挑
/duel query @p：查询用户 p 的 ELO rating
/duel ranklist: 查询排行榜
/duel history @p 查询用户 p 的单挑历史
/duel statics: 查询历史统计"""]
}


def gen_quote(name, preview, messages):
    msg = {
        "type": "Forward",
        "display": {
            "title": name,
            "brief": name,
            "source": name,
            "preview": [preview],
            "summary": "查看{:s}".format(name)
        },
        "nodeList": [
            {
                "senderId": int(self_QQ),
                "time": 0,
                "senderName": "flower",
                "messageChain": [{"type": "Plain", "text": s}],
            }
            for s in messages]
    }
    return msg


def ban(group, plug):
    if not group in groupauth:
        groupauth[group] = set()
    groupauth[group].add(plug)
    syncto('groupauth.json', groupauth)


def active(group, plug):
    groupauth[group].remove(plug)
    syncto('groupauth.json', groupauth)


def requestauth(group, plug):
    try:
        if plug in groupauth[group]:
            return 0
    except KeyError:
        pass
    return 1


def is_admin(qq):
    return str(qq) in admin_QQ


def is_blacklist(qq):
    return str(qq) in blacklist


def is_superadmin(qq):
    return str(qq) == super_admin


def to_admin(qq):
    qq = str(qq)
    if not is_admin(qq):
        admin_QQ.append(qq)
        syncto('admin.json', admin_QQ)


def remove_admin(qq):
    qq = str(qq)
    if is_admin(qq):
        admin_QQ.remove(qq)
        syncto('admin.json', admin_QQ)


def to_blacklist(qq):
    qq = str(qq)
    if not is_blacklist(qq):
        blacklist.append(qq)
        syncto('blacklist.json', blacklist)


def remove_blacklist(qq):
    qq = str(qq)
    if is_blacklist(qq):
        blacklist.remove(qq)
        syncto('blacklist.json', blacklist)
