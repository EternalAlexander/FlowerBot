import random
import requests
import traceback
import urllib

from alicebot import Plugin
from alicebot.adapter.mirai.message import MiraiMessageSegment

from authconfigs import *

HelloMessage = """你好!我是 flower，一个 Codeforces/Atcoder Duel Bot，你可以在这里绑定你的 CF 
账号，向其它绑定了账号的用户发起单挑，而我将作为你们的裁判。具体用法请输入 /help 。 
我的主人是 EternalAlexander(2496097294)，有问题请 qq 咨询。

github 地址：https://github.com/EternalAlexander/FlowerBot
使用框架为 Mirai (https://github.com/mamoe/mirai) 和 Alicebot (https://docs.alicebot.dev/)。
"""

VersionMessage = """最近更新于 2023/10/3
优化了指令解析功能
新的 duel 将会记录通过时间和题目
"""


class Hello(Plugin):
    priority: int = 1
    block: bool = False

    async def handle(self) -> None:
        if not requestauth(self.event.sender.group.id, 'hello'):
            await self.event.reply('在当前群组中未开启此功能')
            return
        message_chain = self.event.message.as_message_chain()
        args = self.event.get_plain_text().split(" ")
        if args[0] == '/hello':
            await self.event.reply(HelloMessage)
        if args[0] == '/news':
            await self.event.reply(VersionMessage)
        if args[0] == '/help' or args[0] == '/helpduel':
            if len(args) == 1:
                s = '本群组中可用的模块如下：\n'
                for plug in plugin_data:
                    if requestauth(self.event.sender.group.id, plug):
                        s += '{:s} '.format(plug)
                s += '\n输入 /help [模块名称] 查询详细用法'
                await self.event.reply(s)
            else:
                plug = args[1]
                if not requestauth(self.event.sender.group.id, plug):
                    await self.event.reply('在当前群组中未开启此功能')
                else:
                    if plug in manuel:
                        msg = gen_quote('{:s} 模块的帮助'.format(plug), '帮助信息', manuel[plug])
                    else:
                        msg = plugin_data[plug]
                    await self.event.reply(msg)

        if args[0] == '/exec':
            qq = str(self.event.sender.id)
            if is_admin(qq):
                p = self.event.get_plain_text()[6:]
                exec(p)
            else:
                await self.event.reply("没有权限")
        if args[0] == '/heartbeat':
            msg1 = MiraiMessageSegment.plain("我的心脏还在跳动着啊")
            await self.event.reply(msg1)
        if args[0] == '/test':
            await self.event.reply('正在测试连接')
            CF = '正常'
            AT = '正常'
            try:
                requests.get('https://codeforces.com/api/user.status?handle=Fefer_Ivan&from=1&count=10',
                             timeout=5).json()
            except:
                CF = '失败'
            try:
                urllib.request.urlopen("https://atcoder.jp", timeout=5)
            except:
                AT = '失败'
                traceback.print_exc()
            s = 'CF:' + CF + '，AT:' + AT
            await self.event.reply(s)
        if args[0] == '/命运的天秤':
            await self.event.reply(str(random.randint(0, 1)))
        if args[0] == '/sayto':
            if is_admin(self.event.sender.id):
                p = message_chain
                w = p[1]['text']
                target = w.strip().split(' ')[1]
                p[1]['text'] = w[w.find(target) + len(target) + 1:]
                await self.event.adapter.sendGroupMessage(target=int(target),
                                                          messageChain=p)

    async def rule(self) -> bool:
        try:
            message_chain = self.event.message.as_message_chain()
            tp = self.event.get_plain_text()
            text = message_chain[1]['text'].strip()
            return text in ['/hello', '/heartbeat',
                            '/命运的天秤', '/test', '/news', '/temp'] or text.startswith(
                '/exec') or text.startswith('/say') or text.startswith('/help')
        except:
            return False
