import json
import time
import httpx
import random
import os.path
import traceback
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, MessageSegment
from nonebot.exception import FinishedException
from nonebot.params import CommandArg

cave = on_command("cave", aliases={"回声洞"})
ctrlGroup = json.load(open("data/ctrl.json"))["control"]
path = os.path.abspath(os.path.dirname("."))


async def downloadImages(message: str):
    cqStart = message.find("[CQ:image")
    print("message", message)
    if cqStart == -1:
        return message
    else:
        url = message[message.find("url=", cqStart) +
                      4:message.find("]", cqStart)]
        imageID = str(time.time())
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            with open(f"data/caveImages/{imageID}.png", "wb") as f:
                f.write(response.read())
        return await downloadImages(
            message.replace(
                message[cqStart:message.find("]", cqStart)],
                f"[[Img:{imageID}]]"
            )
        )


def parseCave(text: str):
    imageIDStart = text.find("[[Img:")
    if imageIDStart == -1:
        return text
    else:
        imageID = text[imageIDStart + 6:text.find("]]]", imageIDStart)]
        imagePath = os.path.join(path, "data", "caveImages", f"{imageID}.png")
        imageCQ = f"[CQ:image,file=file://{imagePath}]"
        return parseCave(
            text.replace(
                f"[[Img:{imageID}]]]",
                str(imageCQ)
            )
        )


@cave.handle()
async def cave_handle(
        bot: Bot,
        event: MessageEvent,
        message: Message = CommandArg()):
    try:
        data = json.load(open("data/cave.data.json", encoding="utf-8"))
        argument = message.extract_plain_text().split(" ")
        if argument[0] == "":
            caveList = data["data"].values()
            caveData = random.choice(list(caveList))
            text = parseCave(caveData["text"])
            senderData = await bot.get_stranger_info(user_id=caveData["sender"])
            await cave.finish(Message(f"""回声洞——（{caveData['id']}）
{text}
——{senderData['nickname']}"""))

        elif argument[0] in ["add", "-a", "添加"]:
            text = await downloadImages(str(message)[argument[0].__len__():].strip())
            data["data"][data["count"]] = {
                "id": data["count"],
                "text": text,
                "sender": event.get_user_id()
            }
            data["count"] += 1
            # 发送通知
            await bot.send_group_msg(
                message=Message((
                    f"「回声洞新投稿（{data['count'] - 1}）」\n"
                    f"来自：{event.get_session_id()}\n"
                    f"内容：{str(message)[argument[0].__len__():].strip()}"
                )),
                group_id=ctrlGroup
            )
            # 写入数据
            json.dump(data, open("data/cave.data.json", "w", encoding="utf-8"))
            await cave.finish(f"回声洞（{data['count'] - 1}）已添加")

        elif argument[0] in ["-g", "查询"]:
            caveData = data["data"][argument[1]]
            text = parseCave(caveData["text"])
            senderData = await bot.get_stranger_info(user_id=caveData["sender"])
            await cave.finish(Message(f"""回声洞——（{caveData['id']}）
{text}
——{senderData['nickname']}"""))

    except FinishedException:
        raise FinishedException()
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup
        )
        await cave.finish("处理失败")