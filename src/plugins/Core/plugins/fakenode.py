import json
import traceback

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
# from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.exception import FinishedException
from nonebot.params import CommandArg

ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
fakenode = on_command("fakenode", aliases={"伪转发"})


@fakenode.handle()
async def fakenodeHandle(
        bot: Bot,
        event: GroupMessageEvent,
        msg: Message = CommandArg()):
    try:
        argument = str(msg).split("\n")
        group = event.get_session_id().split("_")[1]
        message = []
        for argv in argument:
            data = argv.split(":")
            userData = await bot.get_stranger_info(user_id=data[0])
            message += [
                {
                    "type": "node",
                    "data": {
                        "name": userData["nickname"],
                        "uin": data[0].strip(),
                        "content": data[1].strip()
                    }
                }
            ]
        await bot.call_api(
            api="send_group_forward_msg",
            messages=message,
            group_id=group
        )
        await bot.send_group_msg(
            message=f"「新建伪转发」\n用户：{event.get_user_id()}",
            group_id=ctrlGroup
        )
        await bot.call_api(
            api="send_group_forward_msg",
            messages=message,
            group_id=ctrlGroup
        )
        await fakenode.finish()

    except FinishedException:
        raise FinishedException()
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup
        )
        await fakenode.finish("处理失败")

# [HELPSTART]
# !Usage 1 fakenode <QQ号>:<消息>\n<QQ号>:<消息>\n<QQ号>:<消息>\n...
# !Info 1 伪造一个QQ群转发消息并发送到当前群聊
# [HELPEND]