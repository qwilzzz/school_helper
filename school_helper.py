import random
import requests
import json

import vk_api.vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from bot_config import *

class Bot:
    def __init__(self,api_token,group_id):
        self.vk=vk_api.VkApi(token=api_token)
        self.group_id=group_id
        self.long_poll=VkBotLongPoll(self.vk,group_id)
        self.vk_api=self.vk.get_api()

        self.hello = """Привет, я помогу тебе подготовиться к экзаменам! С помощью меня ты можешь сгенерировать вариант по желаемому предмету! Так же я буду присылать тебе материалы с теорией для подготовки."""



    @staticmethod
    def generate_random_id():
        return random.randint(-9223372036854775808,9223372036854775807)

    @staticmethod
    def gen_test(theme):
        with open(f'themes/{theme}', 'r') as file:
            params = file.read()
        r = requests.post(f'https://{theme}-ege.sdamgia.ru/test?a=generate&'+params)
        return r.url

    @staticmethod
    def open_keyboard(keyboard_path):
        if not keyboard_path:
            keyboard_path = 'remove.json'
        with open(f'keyboards/{keyboard_path}', "r", encoding="UTF-8") as keyboard_file:
            return keyboard_file.read()

    def send_msg(self,**kwargs):
        kwargs['random_id']=kwargs.get('random_id',Bot.generate_random_id())
        if 'keyboard' in kwargs:
            kwargs['keyboard'] = Bot.open_keyboard(kwargs['keyboard'])

        self.vk_api.messages.send(**kwargs)

    def handle_command(self, event):
        args = json.loads(event.object.message['payload'])['command']
        if args == "help":
            self.send_msg(peer_id = event.object.message['peer_id'],
                          message = 'Используй "Сгенерировать вариант" для генерации варианта')
        if args == "start":
            self.send_msg(peer_id = event.object.message['peer_id'],
                          message = 'Выберите действие', keyboard = 'main.json')
        if args[0] == 'get_keyboard':
            self.send_msg(peer_id = event.object.message['peer_id'],
                          message = args[2], keyboard = args[1])

        if args[0] == 'gen_test':
            self.send_msg(peer_id = event.object.message['peer_id'],
                          message = f'Вариант создан:\n{self.gen_test(args[1])}')
    def test(self):
        self.send_msg(peer_id=253884576,message=self.hello, keyboard = '')

    def start(self):
        for event in self.long_poll.listen():
            print(event)
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.object.message:
                    payload = event.object.message.get('payload')
                    if payload:
                        self.handle_command(event)
                else:
                    self.send_msg(peer_id = event.object.message['peer_id'],
                                  message = 'Выберите действие', keyboard = 'main.json')
                    

if __name__=='__main__':
    school_helper=Bot(vk_token,group_id)
    school_helper.test()
    school_helper.start()

