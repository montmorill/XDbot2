import json
from nonebot import on_command, get_driver, get_bots
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.params import CommandArg
from . import _lang
from . import _error
import traceback
from .su import su

priority_accout = json.load(open("data/su.priority_accout.json", encoding="utf-8"))
accouts = {}
multiAccoutData = {}
accout_manager = on_command("accout", aliases={"多帐号"})
driver = get_driver()


@su.handle()
async def get_multiaccout_data(bot: Bot, message: Message = CommandArg()):
    try:
        argument = str(message).split(" ")
        if argument[0] in ["ma", "multiaccout", "多账户"]:
            if argument[1] in ["status", "状态"]:
                reply = "「XDbot2 Multi-Accout 账户列表」\n"
                bots = get_bots()
                reply += f"已连接账户：{len(bots.keys())}\n"
                length = 1
                for accout in list(bots.keys()):
                    userData = await bot.get_stranger_info(
                        user_id=(await bots[accout].get_login_info())["user_id"])
                    reply += (
                        f"{length}. {userData['nickname']} ({userData['user_id']})\n")
                    length += 1
                await su.send(reply)
                # 分配情况
                length = 1
                reply = "「XDbot2 Multi-Accout 群聊分配」\n"
                for group in list(multiAccoutData.keys()):
                    reply += f"{length}. {group}: {multiAccoutData[group]}\n"
                    length += 1
                await su.finish(reply)
    except BaseException:
        await _error.report(traceback.format_exc(), su)



@driver.on_bot_connect
@driver.on_bot_disconnect
async def reloadMuiltData():
    global multiAccoutData, bots, accouts
    bots = get_bots()
    accouts = {}
    multiAccoutData = {}
    for key in list(bots.keys()):
        bot = bots[key]
        groups = await bot.get_group_list()
        for group in groups:
            if group["group_id"] not in accouts.keys():
                accouts[group["group_id"]] = [key]
            else:
                accouts[group["group_id"]].append(key)
            if group["group_id"] not in multiAccoutData.keys():
                multiAccoutData[group["group_id"]] = key
            elif key in priority_accout["accouts"]:
                multiAccoutData[group["group_id"]] = key
    json.dump(multiAccoutData, open("data/su.multiaccoutdata.ro.json", "w", encoding="utf-8"))


@accout_manager.handle()
async def mulitaccout_manager(
        event: GroupMessageEvent,
        message: Message = CommandArg()):
    global multiAccoutData
    try:
        argument = str(message).split(" ")
        qq = event.get_user_id()
        if argument[0] == "set":
            if argument[1] in accouts[event.group_id]:
                multiAccoutData[event.group_id] = argument[1]
                json.dump(
                    multiAccoutData, open(
                        "data/su.multiaccoutdata.ro.json", "w", encoding="utf-8"))
                await accout_manager.finish(_lang.text("su.set_accout_success", [argument[1]], qq))
            else:
                await accout_manager.finish(_lang.text("su.accout_not_found"), user=qq)
        elif argument[0] == "list":
            await accout_manager.finish(_lang.text("su.accout_list", [accouts[event.group_id]], qq))
        elif argument[0] == "reload":
            await reloadMuiltData()

    except BaseException:
        await _error.report(traceback.format_exc(), accout_manager)
