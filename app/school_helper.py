import random
import requests
import json
import time

import colorama
colorama.init()

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

import vk_api.vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

APPDIR = "./app"

class Bot:
    def __init__(self,api_token,group_id, logging = False):
        self.vk=vk_api.VkApi(token=api_token)
        self.group_id=group_id
        self.long_poll=VkBotLongPoll(self.vk,group_id)
        self.vk_api=self.vk.get_api()

        self.logging = logging
        self.hello = """Привет, я помогу тебе подготовиться к экзаменам! С помощью меня ты можешь сгенерировать вариант по желаемому предмету! Так же я буду присылать тебе материалы с теорией для подготовки."""



    @staticmethod
    def generate_random_id(): # Генерация случайных id-ов, необязательно, оставь для красоты
        return random.randint(-9223372036854775808,9223372036854775807)

    @staticmethod
    def gen_test(theme): # генерация тестов по теме, ищет в ./themes/, 
                         # файлы с параметрами для предмета совпадают с именами доменов ({предмет}-ege.sdamgia.ru)
        with open(f'{APPDIR}/themes/{theme}', 'r') as file:
            params = file.read()
        r = requests.post(f'https://{theme}-ege.sdamgia.ru/test?a=generate&'+params)
        return r.url

    @staticmethod
    def open_keyboard(keyboard_path): # Загрузить файл с клавиатурой, ищет в ./keyboards/
        if not keyboard_path:
            keyboard_path = 'remove.json'
        with open(f'{APPDIR}/keyboards/{keyboard_path}', "r", encoding="UTF-8") as keyboard_file:
            return keyboard_file.read()

    def send_msg(self,**kwargs): # отправить сообщения, аргументы совпадают с messages.send
        kwargs['random_id']=kwargs.get('random_id',Bot.generate_random_id())
        if 'keyboard' in kwargs:
            kwargs['keyboard'] = Bot.open_keyboard(kwargs['keyboard'])

        self.vk_api.messages.send(**kwargs)

    def handle_command(self, event): # Обработчик команд
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
    def test(self): # Для тестирования
        self.send_msg(peer_id=253884576,message=self.hello, keyboard = '')

    def start(self): # Mainloop
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                self.console_log(event.object,'json')
                if event.object.message:
                    payload = event.object.message.get('payload')
                    if payload:
                        self.handle_command(event)
                else:
                    self.send_msg(peer_id = event.object.message['peer_id'],
                                  message = 'Выберите действие', keyboard = 'main.json')
    
    def console_log(self, data, type):
        if self.logging:
            if type == 'error':
                print(colorama.Fore.RED+data+colorama.Style.RESET_ALL)
            if type == 'json':
                formatted_json = json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False)
                colorful_json = highlight(formatted_json, JsonLexer(), TerminalFormatter())
                print(colorful_json)

                


    def mainloop(self):
        while True:
            try:
                self.start()
            except Exception as ex:
                self.console_log(f'Что-то пошло не так:\n{repr(ex)}','error')
            time.sleep(1)
