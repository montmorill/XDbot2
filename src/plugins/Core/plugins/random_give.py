from time import time
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot import on_message
from . import _lang
from . import _error
from . import _userCtrl
import random
import traceback

random_give = on_message()
latest = time()


@random_give.handle()
async def random_give_handle(event: GroupMessageEvent):
    global latest
    try:
        if time() - latest >= 60 and random.random() <= 0.15:
            reply = _lang.text("random_give.reply", [], event.get_user_id())
            send_reply = False
            length = 1

            if random.random() <= 0.25:
                add_coin = random.randint(0, 25)
                _userCtrl.addItem(event.get_user_id(), "0", add_coin, {})
                reply += f"\n {length}. VimCoin x{add_coin}"
                send_reply = True
                length += 1
            if random.random() <= 0.15:
                add_exp = random.randint(10, 50)
                _userCtrl.addExp(event.get_user_id(), add_exp)
                reply += f"\n {length}. 经验 x{add_exp}"
                send_reply = True
                length += 1
            else:
                _userCtrl.addExp(event.get_user_id(), random.randint(0, 15))
            if random.random() <= 0.05:
                add_role = random.randint(0, 3)
                _userCtrl.addItem(event.get_user_id(), "1", add_role, {})
                reply += f"\n {length}. 二十面骰 x{add_role}"
                send_reply = True
                length += 1

            if send_reply:
                await random_give.send(reply, at_sender=True)
        
        else:
            if random.random() <= 0.15:
                _userCtrl.addExp(event.get_user_id(), random.randint(0, 3))
            

    except BaseException:
        await _error.report(traceback.format_exc())

