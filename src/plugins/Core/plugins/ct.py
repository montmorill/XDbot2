from nonebot.adapters.onebot.v11.bot import Bot
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot import on_command
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
import traceback
import os.path
import json
import math


ct = on_command("ct", aliases={"发言排名"})
ctRecorder = on_message()
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
globalConfig = json.load(open("data/init.json", encoding="utf-8"))["config"]


@ct.handle()
async def ctHandle(
        bot: Bot,
        event: GroupMessageEvent,
        message: Message = CommandArg()):
    try:
        argument = message.extract_plain_text().split(" ")
        groupID = event.get_session_id().split("_")[1]
        if argument[0] == "":
            data = json.load(open("data/ct.globalData.json", encoding="utf-8"))
            users = []
            for key in data.keys():
                inserted = False
                length = 0
                for user in users:
                    if data[key] >= user["count"]:
                        users.insert(
                            length,
                            {
                                "user": key,
                                "count": data[key]
                            }
                        )
                        inserted = True
                        break
                    length += 1
                # 如果用户是目前倒数
                if not inserted:
                    users += [
                        {
                            "user": key,
                            "count": data[key]
                        }
                    ]
            # 生成排名
            nowRank = 0
            length = 0
            myRank = math.inf
            myQQ = event.get_user_id()
            myCount = "暂无数据"
            nowCount = math.inf
            temp0 = 1
            for user in users:
                if user["count"] < nowCount:
                    nowCount = user["count"]
                    nowRank += temp0
                    temp0 = 1
                else:
                    temp0 += 1
                users[length]["rank"] = nowRank
                # 判断是不是自己
                if user['user'] == myQQ:
                    myRank = nowRank
                    myCount = nowCount
                # 增加循环次数
                length += 1
            # 合成文本
            text = "发言排名 —— 全局\n"
            for user in users[:15]:
                text += f"{user['rank']}. {(await bot.get_stranger_info(user_id=user['user']))['nickname']}: {user['count']}\n"
            text += "-" * 25
            text += f"\n{myRank}. {(await bot.get_stranger_info(user_id=myQQ))['nickname']}: {myCount}"
            # 反馈结果
            await ct.finish(text)
        elif argument[0] == "group" or argument[0] == "本群排名":
            data = json.load(open(f"data/ct.{groupID}.json", encoding="utf-8"))
            users = []
            for key in data.keys():
                inserted = False
                length = 0
                for user in users:
                    if data[key] >= user["count"]:
                        users.insert(
                            length,
                            {
                                "user": key,
                                "count": data[key]
                            }
                        )
                        inserted = True
                        break
                    length += 1
                # 如果用户是目前倒数
                if not inserted:
                    users += [
                        {
                            "user": key,
                            "count": data[key]
                        }
                    ]
            # 生成排名
            nowRank = 0
            length = 0
            myRank = math.inf
            myQQ = event.get_user_id()
            myCount = "暂无数据"
            nowCount = math.inf
            temp0 = 1
            for user in users:
                if user["count"] < nowCount:
                    nowCount = user["count"]
                    nowRank += temp0
                    temp0 = 1
                else:
                    temp0 += 1
                users[length]["rank"] = nowRank
                # 判断是不是自己
                if user['user'] == myQQ:
                    myRank = nowRank
                    myCount = nowCount
                # 增加循环次数
                length += 1
            # 合成文本
            text = f"发言排名 —— {groupID}\n"
            for user in users[:15]:
                text += f"{user['rank']}. {(await bot.get_stranger_info(user_id=user['user']))['nickname']}: {user['count']}\n"
            text += "-" * 25
            text += f"\n{myRank}. {(await bot.get_stranger_info(user_id=myQQ))['nickname']}: {myCount}"
            # 反馈结果
            await ct.finish(text)
        else:
            await ct.finish("""Usage：ct [group]""")

    except FinishedException:
        raise FinishedException()
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup)
        await ct.finish("处理失败")


@ctRecorder.handle()
async def ctRecorderHandle(
        bot: Bot,
        event: GroupMessageEvent):
    try:
        # 忽略命令
        for start in globalConfig["command_start"]:
            if event.get_plaintext().startswith(start):
                return
        # 获取数据
        globalData = json.load(open("data/ct.globalData.json"))
        group = event.get_session_id().split("_")[1]
        userID = event.get_user_id()
        if os.path.isfile(f"data/ct.{group}.json"):
            groupData = json.load(open(f"data/ct.{group}.json"))
        else:
            groupData = dict()
        # 修改数据
        if userID not in globalData.keys():
            globalData[userID] = 1
        else:
            globalData[userID] += 1
        if userID not in groupData.keys():
            groupData[userID] = 1
        else:
            groupData[userID] += 1
        # 保存数据
        json.dump(globalData, open("data/ct.globalData.json", "w"))
        json.dump(groupData, open(f"data/ct.{group}.json", "w"))

    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup
        )