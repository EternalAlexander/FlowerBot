import asyncio
import functools
import json
import pygame
import random
import traceback
from alicebot import Plugin
from alicebot.adapter.mirai.message import MiraiMessageSegment

from authconfigs import *
from filemanage import *

pygame.init()

font = pygame.font.Font(None, 50)

PATH = 'plugins//data//wordle//'

with open(PATH + 'words_dictionary.json', 'r') as file:
    dic = list(json.loads(file.read()))
dic2 = {}
meaning = {}


def reload():
    global dic, dic2, meaning
    with open(PATH + 'words_dictionary.json', 'r') as file:
        dic = list(json.loads(file.read()))
    with open(PATH + 'words1.txt', 'r', encoding='UTF-8') as file:
        a = file.readlines()
        for x in a:
            s = x.split('\t')[0].lower()
            if '-' in s or s == 'caregiver':
                continue
            l = len(s)
            if not l in dic2:
                dic2[l] = []
            dic2[l].append(s.upper())
            meaning[s.upper()] = x[len(s) + 1:]
    for i in range(4, 12):
        dic2[i] = list(set(dic2[i]))


reload()


def cmp(x, y):
    return len(y) - len(x)


def pattern(ori, gue):
    s1 = []
    pat = [0 for i in range(len(ori))]
    for j in range(len(gue)):
        if ori[j] != gue[j]:
            s1 += ori[j]
    for j in range(len(ori)):
        if gue[j] == ori[j]:
            pat[j] = 2
        elif gue[j] in s1:
            s1.remove(gue[j])
            pat[j] = 1
    return pat


def hash1(pat):
    h = 0
    for x in range(len(pat)):
        h = h * 3 + pat[x]
    return h


class Wordle():
    def __init__(self, word, hardmode=0):

        if not hardmode:
            self.word = word.upper()
            self.len = len(word)
        else:
            self.word = dic2[word]
            self.len = word
        self.cnt = 0
        self.records = []
        self.hardmode = hardmode

    def guess(self, word):
        if not word.lower() in dic:
            return -2
        if not len(word) == self.len:
            return -3
        word = word.upper()
        self.records.append(word)
        self.cnt += 1
        if not self.hardmode:
            if word == self.word:
                return 1
            if self.cnt == 6:
                return -1
            return 0
        else:
            res = {}
            for x in self.word:
                pat = pattern(x, word)
                h = hash1(pat)
                if not h in res:
                    res[h] = []
                res[h].append(x)
            lis = [res[x] for x in res]
            lis.sort(key=functools.cmp_to_key(cmp))
            self.word = lis[0]
            lis = [x for x in lis if x[0] != word]
            if lis:
                self.word = random.choice(lis[:int(7 / self.cnt)])
            if word == self.word[0] and len(self.word) == 1:
                return 1
            if self.cnt == 6:
                return -1
            print("rem: " + str(len(self.word)))
            return 0

    def api(self):
        s = ''
        for i in range(self.cnt):
            if not self.hardmode:
                pat = pattern(self.word, self.records[i])
            else:
                pat = pattern(self.word[0], self.records[i])
            s += str(pat) + '\n'
        return s

    def answer(self):
        if self.hardmode:
            return self.word[0]
        return self.word

    def generate_picture(self, path):
        screen = pygame.surface.Surface([60 * self.len + 10, 60 * self.cnt + 10])
        colBG, col0, col1, col2 = [255, 255, 255], [180, 180, 180], [255, 150, 0], [0, 255, 0]
        if self.hardmode:
            colBG, col0, col1, col2 = [0, 0, 0], [120, 120, 120], [205, 120, 0], [0, 205, 0]
        screen.fill(colBG)
        for i in range(self.cnt):
            if not self.hardmode:
                pat = pattern(self.word, self.records[i])
            else:
                pat = pattern(self.word[0], self.records[i])
            for j in range(len(self.records[i])):
                if pat[j] == 2:
                    color = col2
                elif pat[j] == 1:
                    color = col1
                else:
                    color = col0

                pygame.draw.rect(screen, color, [60 * j + 10, 60 * i + 10, 50, 50], 0, 5)
                if self.hardmode:
                    if pat[j] == 2: pygame.draw.rect(screen, [255, 255, 0], [60 * j + 10, 60 * i + 10, 50, 50], 3, 5)
                    if pat[j] == 1: pygame.draw.rect(screen, [255, 0, 0], [60 * j + 10, 60 * i + 10, 50, 50], 3, 5)
                    if pat[j] == 0: pygame.draw.rect(screen, [0, 0, 255], [60 * j + 10, 60 * i + 10, 50, 50], 3, 5)
                txtimg = font.render(self.records[i][j], True, [0, 0, 0])
                screen.blit(txtimg, [60 * j + 20, 60 * i + 20])
        pygame.image.save(screen, path)


def new_wordle(length, hard=0):
    if not 4 <= length <= 11:
        return -1
    if not hard:
        word = random.choice(dic2[length])
        return Wordle(word)
    else:
        return Wordle(length, 1)


def word(w):
    return w + ' ' + meaning[w]


current = syncfrom('wordle.json', {})

lock = asyncio.Lock()

print('fin wordle')


class WordlePlugin(Plugin):
    priority: int = 1
    block: bool = False

    async def handle(self) -> None:
        async with lock:
            if not requestauth(self.event.sender.group.id, 'wordle'):
                await self.event.reply('在当前群组中未开启此功能')
                return
            global current
            message_chain = self.event.message.as_message_chain()
            text = message_chain[1]['text'].strip()
            args = text.split(' ')
            try:
                sender = self.event.sender.group.id
                if not sender in current:
                    current[sender] = None
                if len(args) == 1:
                    await self.event.reply('''/wordle 用法：
    /wordle new x [serious] 开始新游戏，单词长度为 x。若填写 serious 则开始严肃模式。
    /wordle guess [单词] 猜测单词
    /wordle remain 查看剩下的字母
    /wordle giveup 放弃当前游戏''')
                    return
                if args[1] == 'reload':
                    if is_admin(self.event.sender.id):
                        try:
                            reload()
                            await self.event.reply('重载成功')
                        except BaseException:
                            await self.event.reply('重载失败，见 flower.log')
                    else:
                        await self.event.reply('没有权限')
                if args[1] == 'giveup':
                    if not current[sender]:
                        await self.event.reply('没有进行中的 Wordle')
                    else:
                        await self.event.reply('你放弃了，正确答案是 ' + word(current[sender].answer()))
                        current[sender] = None
                    syncto('wordle.json', current)
                elif args[1] == 'new':
                    length = int(args[2])
                    if length < 4 or length > 11:
                        await self.event.reply('长度必须是 4~11 的整数')
                        return
                    if current[sender]:
                        await self.event.reply('有一个进行中的 Wordle')
                        return
                    else:
                        if len(args) == 4 and args[3] == 'serious':
                            current[sender] = new_wordle(length, 1)
                            await self.event.reply(
                                '好的，让我们严肃地一决胜负吧。\n输入 /wordle guess [单词] 开始第一次猜测。你有 6 次机会。')
                        else:
                            current[sender] = new_wordle(length)
                            await self.event.reply(
                                '开始了一局新的 Wordle，输入 /wordle guess [单词] 开始第一次猜测。你有 6 次机会。')
                        syncto('wordle.json', current)
                        return
                elif args[1] == 'remain':
                    if not current[sender]:
                        await self.event.reply('没有进行中的 Wordle')
                    s = ''
                    for x in 'abcdefghijklmnopqrstuvwxyz'.upper():
                        flag = 1
                        for j in current[sender].records:
                            if x in j:
                                flag = 0
                        if flag:
                            s += x + ' '
                    await self.event.reply('未使用过的字母有:' + s)
                elif args[1] == 'api':
                    if not current[sender]:
                        await self.event.reply('没有进行中的 Wordle')
                    else:
                        await self.event.reply(current[sender].api())
                elif args[1] == 'guess':
                    if not current[sender]:
                        await self.event.reply('没有进行中的 Wordle')
                    else:
                        val = current[sender].guess(args[2])
                        if val == -2:
                            await self.event.reply('抱歉，我不认识你猜测的这个单词...')
                            return
                        elif val == -3:
                            await self.event.reply('请输入一个长度为 ' + str(current[sender].len) + '的单词')
                            return
                        print('step 1')
                        current[sender].generate_picture('wordle.png')
                        msg = MiraiMessageSegment.image(
                            path=MAINPATH + 'wordle.png')
                        await self.event.reply(msg)
                        if val == 0:
                            await self.event.reply('你还有 ' + str(6 - current[sender].cnt) + '次机会')
                            syncto('wordle.json', current)
                            return
                        elif val == -1:
                            await self.event.reply('你用完了所有机会，你失败了。答案是 ' + word(current[sender].answer()))
                            current[sender] = None
                            syncto('wordle.json', current)
                            return
                        elif val == 1:
                            s1 = ''
                            s = str(self.event.sender.id)
                            await self.event.reply(word(current[sender].answer()) + '，你猜中了答案！' + s1)
                            current[sender] = None
                            syncto('wordle.json', current)
                            return

            except:
                traceback.print_exc()

    async def rule(self) -> bool:
        try:
            message_chain = self.event.message.as_message_chain()
            tp = self.event.get_plain_text()
            text = message_chain[1]['text'].strip()
            return text.startswith('/wordle')
        except:
            return False
