import datetime
import json

import disnake
from disnake.ext.commands import Bot

from tools.logger import Log
from tools.draw_types import DrawTypes
from tools.BGConsole import BGC
def set_current_draw(id: int, type: DrawTypes, text: str, award: str, time: float, need_count: float, announcement: int):
    with open("bot_config.json", 'r') as f:
        loader = json.load(f)
        f.close()
    if type == DrawTypes.VOICE:
        fix_type = 'voice'
    elif type == DrawTypes.TEXT:
        fix_type = 'text'
    else:
        fix_type = None
    with open("bot_config.json", 'w') as f:
        loader['config']['current_draw']['id'] = id
        loader['config']['current_draw']['type'] = fix_type
        loader['config']['current_draw']['text'] = text
        loader['config']['current_draw']['award'] = award
        loader['config']['current_draw']['time'] = time
        loader['config']['current_draw']['need_count'] = need_count
        loader['config']['current_draw']['announcement'] = announcement
        json.dump(loader, f)
        f.close()

def get_current_draw():
    with open("bot_config.json", 'r') as f:
        loader = json.load(f)
        f.close()
    return loader['config']['current_draw']

def convert_boolean(value: bool) -> int:
    return 1 if value else 0

def set_bot_token(token: str):
    with open("bot_config.json", 'r') as f:
        loader = json.load(f)
        f.close()
    with open("bot_config.json", 'w') as f:
        loader["config"]["bot_token"] = token
        json.dump(loader, f)
        f.close()

def set_max_winners(count: int):
    with open("bot_config.json", 'r') as f:
        loader = json.load(f)
        f.close()
    with open("bot_config.json", 'w') as f:
        loader["config"]["max_winners"] = count
        json.dump(loader, f)
        f.close()

def get_max_winners():
    with open("bot_config.json", 'r') as f:
        loader = json.load(f)
        f.close()
    if loader["config"]["max_winners"] != None:
        return loader["config"]["max_winners"]
def set_draw_channel(channel_id: int):
    with open("bot_config.json", 'r') as f:
        loader = json.load(f)
        f.close()
    with open("bot_config.json", 'w') as f:
        loader["config"]["draw_channel"] = channel_id
        json.dump(loader, f)
        f.close()

def get_draw_channel():
    with open("bot_config.json", 'r') as f:
        loader = json.load(f)
        f.close()
    if loader["config"]["draw_channel"] != None:
        return loader["config"]["draw_channel"]
    Log.e("get_draw_channel", "Value of 'draw_channel' key in bot_config.json is empty. Call #set_draw_chan <channel> command in discord chat to fix it")
    raise Exception("Value of 'draw_channel' key in bot_config.json is empty. Call #set_draw_chan <channel> command in discord chat to fix it")


def get_bot_token():
    with open("bot_config.json", 'r') as f:
        loader = json.load(f)
        f.close()
    if loader["config"]["bot_token"] != None:
        return loader["config"]["bot_token"]
    new_token = BGC.scan(label="В файле конфигурации bot_config.json отсутствует токен. Введи токен бота здесь /> ", label_color=BGC.Color.CRIMSON)
    set_bot_token(new_token)
    return new_token

def create_error_embed(msg: str):
    return disnake.Embed(
        title="Что-то пошло не так!",
        description=msg,
        color=disnake.Color.red()
    )

async def create_anno_embed(bot: Bot, text: str, award: str, time: float, need: float, type: DrawTypes, channel: int):
    moscow_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    new_time = moscow_time + datetime.timedelta(minutes=time)
    new_time_str = new_time.strftime("%Y-%m-%d %H:%M")
    if type == DrawTypes.TEXT:
        return disnake.Embed(
        title=':tada: Хэй, друзья, объявлен новый розыгрыш!',
        description=f"{text}\n\n:confetti_ball: Награда: `{award}`\n:question: Условие: Нужно написать {int(need)} сообщений в канале {(await bot.fetch_channel(channel)).mention}\n:date: Срок: До {new_time_str} по МСК",
        color=disnake.Color.random()
    )
    if type == DrawTypes.VOICE:
        return disnake.Embed(
        title=':tada: Хэй, друзья, объявлен новый розыгрыш!',
        description=f"{text}\n\n:confetti_ball: Награда: `{award}`\n:question: Условие: Нужно пробыть {int(need)} минут в канале {(await bot.fetch_channel(channel)).mention} с включенным микрофоном\n:date: Срок: До {new_time_str} по МСК",
        color=disnake.Color.random()
    )
