import json
import traceback
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message
from nonebot.exception import FinishedException
from nonebot.params import CommandArg

ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
command_start = "/"
help = on_command("help", aliases={"帮助"})


@help.handle()
async def helpHandle(bot: Bot, message: Message = CommandArg()):
    try:
        argument = message.extract_plain_text()
        reply = ""
        commands = json.load(open("data/help.json", encoding="utf-8"))
        if argument == "":
            reply = "命令列表 —— XDbot2\n"
            for key in list(commands.keys()):
                reply += f"[√] {key}：{commands[key]['msg']}\n"
            reply += "使用 /help <命令> 获取更多信息"
        elif argument == "list":
            for key in list(commands.keys()):
                for u in commands[key]["usage"]:
                    reply += f"{command_start}{u}\n"
        else:
            usage = ""
            length = 1
            for u in commands[argument]['usage']:
                usage += f"  {length}. {u}\n"
                length += 1
            reply = (
                f"\n说明：{commands[argument]['info']}\n"
                # f"来源：{commands[argument]['from']}\n"
                f"用法（{length - 1}）：\n{usage}"
            )
        await help.finish(reply)
    except FinishedException:
        raise FinishedException()
    except Exception:
        await bot.send_group_msg(message=traceback.format_exc(),
                                 group_id=ctrlGroup)


# [HELPSTART] Version: 2
# Command: help
# Usage: help：查看指令列表
# Usage: help list：查看所有指令的所有用法
# Usage: help <指令名>：查看指定指令的用法
# Info: 查询指定命令说明，若未指定指令名，则显示全部命令用法
# Msg: 查看指令帮助
# [END]

# !Usage 1 help [指令名]

# [HELPEND]

# ########### help的写法 ############
#
# 1. # [HELPSTART]
# `命令帮助开始 (注意空格不能丢,后面也最好别加空格,下同)
#
# 2. # !Usage num usage
# `对命令格式的说明 (可以有多个不同num的 !Usage)
# num 为在此插件中的命令编号(一个插件可以添加多条命令) 对应下文Info的信息
# usage 为命令格式 不需要写前缀 参数之间按空格分割 一般为 command <arg1> <arg2> ...
#
# 3. # !Info num information
# `对命令作用的说明 (可以有多个不同num的 !Info)
# num 为在此插件中的命令编号 对应上文Usage的信息
# information 为命令作用说明 可以使用\n换行
#
# 4. # [HELPEND]
# `命令帮助结束
#
# 警告：Usage一定要写在相同num的Info前面，一个num必须同时有Usage和Info，不然我也不知道会出什么bug
#
###################################