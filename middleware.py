import time
from telebot import BaseMiddleware
from telebot.types import Message
from telebot.handler_backends import CancelUpdate


class LimitedTimeMiddleware(BaseMiddleware):
    def __init__(self, bot, limit_seconds=3):
        super().__init__()
        self.bot = bot
        self.limit = limit_seconds
        self.last_time = {}
        self.update_types = ['message', 'callback_query']

    def pre_process(self, message: Message, data: dict):
        user_id = message.from_user.id
        current_time = time.time()

        if user_id in self.last_time:
            time_delta = current_time - self.last_time[user_id]
            if time_delta < self.limit:
                self.last_time[user_id] = current_time
                self.bot.send_message(message.chat.id, f'Отправляйте запросы  не чаще чем раз в 3 секунды')
                return CancelUpdate()

        self.last_time[user_id] = current_time

    def post_process(self, message: Message, data: dict, exception):
        pass
