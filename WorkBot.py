import telebot
from telebot import types
import os
import time
import works
from telebot.states import StatesGroup, State

token = '7988828975:AAFbKaz33H6kD3Mt5aXfJ-hxBwtlFkIWPuM'

bot = telebot.TeleBot(token)

MAIN_MENU = 0
FIRST_WORK_MENU = 1
ADD_WORK_MENU = 2

count_price = 0



@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📋 Главное меню")
    btn2 = types.KeyboardButton("ℹ️ Информация")
    btn3 = types.KeyboardButton("ℹ️️ подсчет зарплаты")
    btn4 = types.KeyboardButton("ℹ️️ итог за сутки")
    btn5 = types.KeyboardButton("ℹ️️ итог за месяц")
    btn6 = types.KeyboardButton("ℹ️ итог за все время")
    markup.add(btn1, btn2, btn3,btn4,btn5,btn6)

    bot.send_message(message.chat.id, "Добро пожаловать! Выберите пункт меню:", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def handle_text(message, massage=None):
    if message.text == "📋 Главное меню":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("📋 Главное меню")
        btn2 = types.KeyboardButton("ℹ️ Информация")
        btn3 = types.KeyboardButton("ℹ️️ начать подсчет зарплаты")
        btn4 = types.KeyboardButton("ℹ️️ итог за сутки")
        btn5 = types.KeyboardButton("ℹ️️ итог за месяц")
        btn6 = types.KeyboardButton("ℹ️ итог за все время")
        markup.add(btn1, btn2, btn3,btn4,btn5,btn6)


        bot.send_message(message.chat.id, "Добро пожаловать! Выберите пункт меню:", reply_markup=markup)


    elif message.text == "ℹ️ Информация":

        bot.send_message(message.chat.id, "Этот бот создан для подсчета зарплаты самозанятых монтажников МГТС.\n\n"
                                          "-Вы можете начать подсчет зарплаты в меню нажав кнопку 'ℹ️️ начать подсчет зарплаты'.\n\n"
                                          "-Вы можете посмотреть итог за сутки нажав кнопку 'ℹ️️ итог за сутки'.\n\n"
                                          "-Вы можете посмотреть итог за месяц нажав кнопку 'ℹ️️ итог за месяц'.\n\n"
                                          "-Вы можете посмотреть итог за все время нажав кнопку 'ℹ️ итог за все время'.\n\n"
                                          "-Вы можете вернутся в начальное меню нажав кнопку '📋 Главное меню'.\n\n"
                                          'Хорошего дня!'
                        )
   # elif massage.text == "ℹ️️ начать подсчет зарплаты":





        


bot.polling(none_stop=True)