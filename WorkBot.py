import telebot
from telebot import types
import os
import time
import works
from telebot.states import StatesGroup, State

token = '7988828975:AAFbKaz33H6kD3Mt5aXfJ-hxBwtlFkIWPuM'

bot = telebot.TeleBot(token)

MAIN_MENU = 0 # главное меню
FIRST_WORK_MENU = 1 # меню работ
ADD_WORK_MENU = 2 # меню доюавления работ



user_state = {}

count_price = int()
count_all = int()



@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_state[user_id] = MAIN_MENU

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📋 Главное меню")
    btn2 = types.KeyboardButton("ℹ️ Информация")
    btn3 = types.KeyboardButton("ℹ️️ начать подсчет зарплаты")
    btn4 = types.KeyboardButton("ℹ️️ итог за сутки")
    btn5 = types.KeyboardButton("ℹ️️ итог за месяц")
    btn6 = types.KeyboardButton("ℹ️ итог за все время")
    markup.add(btn1, btn2, btn3,btn4,btn5,btn6)

    bot.send_message(message.chat.id, "Добро пожаловать! Выберите пункт меню:", reply_markup=markup)




@bot.message_handler(content_types=['text'])
def handle_text(message, massage=None, count_all=int(), count_price=int()):
    if message.text == "📋 Главное меню":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("📋 Главное меню")
        btn2 = types.KeyboardButton("ℹ️ Информация")
        btn3 = types.KeyboardButton("ℹ️️ начать подсчет зарплаты")
        btn4 = types.KeyboardButton("ℹ️️ итог за месяц")
        btn5 = types.KeyboardButton("ℹ️ итог за все время")
        markup.add(btn1, btn2, btn3,btn4,btn5)


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

    elif message.text == "ℹ️️ начать подсчет зарплаты":
        user_state[message.from_user.id] = FIRST_WORK_MENU
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bt1 = types.KeyboardButton("добавление выполненых работ")
        bt2 = types.KeyboardButton("обнуление мессяца/сохранение итогов")
        bt3 = types.KeyboardButton("📋 Главное меню")
        markup.add(bt1, bt2, bt3)

        bot.send_message(message.chat.id, "Выберите тип выполненной работы или выход в главное меню:", reply_markup=markup)

    elif message.text == "добавление выполненых работ":
        user_state[message.from_user.id] = ADD_WORK_MENU
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_1 = types.KeyboardButton("подключение коннектор")
        btn_2 = types.KeyboardButton("подключение сварка")
        btn_3 = types.KeyboardButton("подключение доп")
        btn_4 = types.KeyboardButton("кроссировка")
        btn_5 = types.KeyboardButton("доплата")
        btn_6 = types.KeyboardButton("обслуживание")
        btn_7 = types.KeyboardButton("обслуживание область")
        btn_8 = types.KeyboardButton("замена оборудования")
        btn_9 = types.KeyboardButton("подключение кабель проложен")
        btn_10 = types.KeyboardButton("подключение интернета")
        btn_11 = types.KeyboardButton("подключение тв")
        btn_12 = types.KeyboardButton("доставка симкарты")
        btn_13 = types.KeyboardButton("демонтаж онт")
        btn_14 = types.KeyboardButton("демонтаж прочих")
        btn_15 = types.KeyboardButton("камера")
        btn_16 = types.KeyboardButton("📋 Главное меню")
        markup.add(btn_1, btn_2, btn_3, btn_4, btn_5, btn_6, btn_7, btn_8, btn_9, btn_10, btn_11, btn_12, btn_13, btn_14, btn_15, btn_16)

        bot.send_message(message.chat.id, "Выберите тип выполненной работы или выход в главное меню:",
                         reply_markup=markup)

    elif message.text == "ℹ️️ итог за месяц":
        bot.send_message(message.chat.id, f'сумма за месяц: {count_price} руб.')

    elif message.text == "ℹ️ итог за все время":
        bot.send_message(message.chat.id, f'сумма за все время: {count_all} руб.')

    elif message.text == "обнуление мессяца/сохранение итогов":
        count_all += count_price
        count_price = int(0)
        bot.send_message(message.chat.id, f'месяц обнулен. сумма: {count_price} руб. \n'
                                          f'итог за все время: {count_all} руб. \n'f'')


        # if message.text == "основные работы":
        #     user_state[message.from_user.id] = ADD_WORK_MENU
        #     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        #     btn_1 = types.KeyboardButton("подключение коннектор")
        #     btn_2 = types.KeyboardButton("подключение сварка")
        #     btn_3 = types.KeyboardButton("подключение доп")
        #     btn_4 = types.KeyboardButton("кроссировка")
        #     btn_5 = types.KeyboardButton("доплата")
        #     btn_6 = types.KeyboardButton("обслуживание")
        #     btn_7 = types.KeyboardButton("обслуживание область")
        #     btn_8 = types.KeyboardButton("замена оборудования")
        #     btn_9 = types.KeyboardButton("подключение кабель проложен")
        #     btn_10 = types.KeyboardButton("назад")
        #     btn_11 = types.KeyboardButton("главное меню")
        #     markup.add(btn_1, btn_2, btn_3, btn_4, btn_5, btn_6, btn_7, btn_8, btn_9, btn_10, btn_11)
        #
        #     bot.send_message(message.chat.id, "Выберите тип выполненной работы или выход в главное меню:", reply_markup=markup)









bot.polling(none_stop=True)