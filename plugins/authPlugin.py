import traceback
from authconfigs import *
from alicebot import Plugin
from alicebot.exceptions import GetEventTimeout
from alicebot.adapter.mirai.message import MiraiMessage, MiraiMessageSegment


class AuthPlugin(Plugin):
    priority: int = 0
    block: bool = False

    async def handle(self) -> None:
        args = self.event.get_plain_text().split(" ")
        message_chain = self.event.message.as_message_chain()
        if is_blacklist(self.event.sender.id):
            self.stop()
            return

        try:
            if args[0] == '/manage':

                if args[1] == 'enable':
                    if is_admin(self.event.sender.id):
                        plug = args[2]
                        if not plug in plugin_data:
                            await self.event.reply('没有这个模块')
                            return
                        active(self.event.sender.group.id,plug)
                        await self.event.reply('在当前群组中开启了 {:s} 模块'.format(plug))
                    else:
                        await self.event.reply('没有权限')

                if args[1] == 'disable':
                    if is_admin(self.event.sender.id):
                        plug = args[2]
                        if not plug in plugin_data:
                            await self.event.reply('没有这个模块')
                            return
                        if plug in permanent:
                            await self.event.reply('这个不能关啊')
                            return
                        ban(self.event.sender.group.id,plug)
                        await self.event.reply('在当前群组中关闭了 {:s} 模块'.format(plug))
                    else:
                        await self.event.reply('没有权限')

                if args[1] == 'blacklist':
                    if is_admin(self.event.sender.id):
                        print(message_chain)
                        target = str(message_chain[2]['target'])

                        if args[2] == 'add':
                            if target == self_QQ:
                                await self.event.reply('你为什么要这样做？')
                                return
                            if is_admin(target):
                                await self.event.reply('可是这是一位管理，我不能无视他的指令'.format())
                                return
                            to_blacklist(target)
                            await self.event.reply('哦哦，好的。不再响应 {:s} 的指令。'.format(target))
                        elif args[2] == 'remove':
                            remove_blacklist(target)
                            await self.event.reply('哦哦，好的。开始响应 {:s} 的指令。'.format(target))
                    else:
                        await self.event.reply('没有权限')

                if args[1] == 'admin':
                    if is_superadmin(self.event.sender.id):
                        target = str(message_chain[2]['target'])
                        if args[2] == 'add':
                            to_admin(target)
                            await self.event.reply('哦哦，好的。已经将 {:s} 设置为管理'.format(target))
                        elif args[2] == 'remove':
                            remove_admin(target)
                            await self.event.reply('哦哦，好的。已经将 {:s} 取消管理'.format(target))
                    else:
                        await self.event.reply('没有权限')

        except BaseException:
            traceback.print_exc()

    async def rule(self) -> bool:
        try:
            assert self.event.sender.group.id
            return True
        except:
            return False
