import json
from tools.draw_types import DrawTypes
def set_current_draw(id: int, type: DrawTypes):
    with open("bot_config.json", 'r') as f:
        loader = json.load(f)
        f.close()
    with open("bot_config.json", 'w') as f:
        loader['config']['current_draw']['id'] = id
        loader['config']['current_draw']['type'] = type
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
def get_bot_token():
    with open("bot_config.json", 'r') as f:
        loader = json.load(f)
        f.close()
    if loader["config"]["bot_token"] != None:
        return loader["config"]["bot_token"]
    new_token = str(input("В файле конфигурации bot_config.json отсутствует токен. Введи токен бота здесь /> "))
    set_bot_token(new_token)
    return new_token
