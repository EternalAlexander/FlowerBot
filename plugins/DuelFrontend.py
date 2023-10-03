import asyncio
import traceback

from alicebot import Plugin
from authconfigs import *
import authPlugin
from alicebot.adapter.mirai.message import MiraiMessage, MiraiMessageSegment
from FlowerCore import executer


def to_text(message_chain):
    s = ''
    for x in message_chain:
        if x['type'] == 'Plain':
            s += x['text']
        if x['type'] == 'At':
            s += str(x['target'])
    return s


try:
    executer.Flower.init()
except:
    traceback.print_exc()

lock = asyncio.Lock()


class DuelFrontend(Plugin):
    priority: int = 1
    block: bool = False

    async def handle(self) -> None:
        """
        if not requestauth(self.event.sender.group.id, 'duel'):
            await self.event.reply('在当前群组中未开启此功能')
            return
        """
        async with lock:
            message_chain = self.event.message.as_message_chain()
            text = to_text(message_chain)
            command = executer.interpret(text)
            if not command[-1]:
                msg = '本条指令被解析为：/'
                for x in command[1]: msg += x + ' '
                await self.event.reply(msg)
            if command[1] == ['duel', 'judge']:
                await self.event.reply('正在判定结果')
            statement = executer.execute_command(command, self.event.sender.id)
            if type(statement) == dict:
                msg = gen_quote(statement['title'], statement['brief'], [statement['text']])
                await self.event.reply(msg)
            else:
                await self.event.reply(statement)

    async def rule(self) -> bool:
        try:
            message_chain = self.event.message.as_message_chain()
            text = to_text(message_chain)
            return text.startswith('/bind') or text.startswith('/duel')
        except:
            return False
