import os
import telebot
from telebot import types
import sqlite3
from datetime import datetime
from flask import Flask, request
from telebot import apihelper

from token_id import id_admin, TOKEN
from works import WORKS
from Paid_works import Paid_Works
from middleware import LimitedTimeMiddleware

TOKEN = TOKEN.strip()

# Абсолютный путь к базе данных (исправляет NameError)
DB_PATH = '/home/Winreii/work_bot/salary.db'

apihelper.proxy = {'https': 'http://proxy.server:3128'}
bot = telebot.TeleBot(TOKEN, threaded=False, use_class_middlewares=True)
bot.setup_middleware(
    LimitedTimeMiddleware(bot)
)
app = Flask(__name__)

@app.route('/', methods=['GET'])
def health_check():
    '''Метод для проверки работаспособности приложения и бота'''
    return 'Бот работает нормально!', 200

WEBHOOK_URL = f"https://winreii.pythonanywhere.com/{TOKEN}"

@app.route(f'/{TOKEN}', methods=['POST'])
def redirect_message():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return 'Forbidden', 403


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS paid_works
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER,
                          number TEXT,
                          price INTEGER,
                          date TEXT,
                          month INTEGER,
                          year INTEGER,
                          FOREIGN KEY(user_id) REFERENCES users(user_id))''')

    # Таблица пользователей
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id INTEGER PRIMARY KEY,
                      username TEXT,
                      first_name TEXT,
                      last_name TEXT,
                      register_date TEXT)''')

    # Таблица работ
    cursor.execute('''CREATE TABLE IF NOT EXISTS works
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      work_type TEXT,
                      price INTEGER,
                      date TEXT,
                      month INTEGER,
                      year INTEGER,
                      FOREIGN KEY(user_id) REFERENCES users(user_id))''')

    # Таблица месячных итогов
    cursor.execute('''CREATE TABLE IF NOT EXISTS monthly_totals
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      month INTEGER,
                      year INTEGER,
                      total INTEGER,
                      save_date TEXT,
                      FOREIGN KEY(user_id) REFERENCES users(user_id))''')

    conn.commit()
    conn.close()


init_db()

# Состояния бота
MAIN_MENU = 0
WORK_MENU = 1
ADD_WORK_MENU = 2
PAID_WORK_MENU = 3
ADD_PAID_WORK_MENU = 4

# Глобальный словарь для хранения состояний пользователей
user_states = {}
# Глобальный словарь для временного хранения данных ввода
user_data = {}


# Функции для работы с базой данных
def get_or_create_user(user_id, username, first_name, last_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        register_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                       (user_id, username, first_name, last_name, register_date))
        conn.commit()

    conn.close()


def add_paid_work(user_id, number, total_amount):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    number = str(number)

    calculator = Paid_Works(number=number)
    price = calculator.calculate_kp(total=int(total_amount))

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")
    month = now.month
    year = now.year

    cursor.execute("INSERT INTO paid_works (user_id, number, price, date, month, year) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, number, price, date_str, month, year))

    conn.commit()
    conn.close()
    return price

def db_delete_last_paid_work(user_id):
    """Удаляет последнюю внесенную дополнительную работу пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, number, price FROM paid_works
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,))
    last_work = cursor.fetchone()

    if last_work:
        work_id, number, price = last_work
        cursor.execute("DELETE FROM paid_works WHERE id = ?", (work_id,))
        conn.commit()
        conn.close()
        return number, price
    else:
        conn.close()
        return None, 0


def get_all_paid_works(user_id):
    """Получает список всех дополнительных работ пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT number, price, date FROM paid_works
        WHERE user_id = ?
        ORDER BY id ASC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_work(user_id, work_type):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    price = WORKS[work_type]
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")
    month = now.month
    year = now.year

    cursor.execute("INSERT INTO works (user_id, work_type, price, date, month, year) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, work_type, price, date_str, month, year))

    conn.commit()
    conn.close()
    return price


def get_month_total(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    now = datetime.now()
    cursor.execute("""
        SELECT COALESCE(SUM(price), 0)
        FROM works
        WHERE user_id=? AND month=? AND year=?
    """, (user_id, now.month, now.year))

    total = cursor.fetchone()[0]
    conn.close()
    return total


def get_all_time_total(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(price) FROM works WHERE user_id=?", (user_id,))
    works_total = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(total) FROM monthly_totals WHERE user_id=?", (user_id,))
    monthly_total = cursor.fetchone()[0] or 0

    conn.close()
    return works_total + monthly_total


def save_month(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    now = datetime.now()
    month = now.month
    year = now.year
    save_date = now.strftime("%Y-%m-%d %H:%M:%S")

    total = get_month_total(user_id)

    if total > 0:
        cursor.execute("INSERT INTO monthly_totals (user_id, month, year, total, save_date) VALUES (?, ?, ?, ?, ?)",
                       (user_id, month, year, total, save_date))

        cursor.execute("DELETE FROM works WHERE user_id=? AND month=? AND year=?",
                       (user_id, month, year))

        conn.commit()
        conn.close()
        return total

    conn.close()
    return 0

def db_delete_last_work(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, work_type, price from works
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,))
    last_work = cursor.fetchone()

    if last_work:
        work_id, work_type, price = last_work
        cursor.execute("DELETE FROM works WHERE id = ?", (work_id,))
        conn.commit()
        conn.close()
        return work_type, price
    else:
        conn.close()
        return None, 0


# Обработчики команд
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_states[user_id] = MAIN_MENU

    get_or_create_user(user_id, message.from_user.username,
                       message.from_user.first_name, message.from_user.last_name)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        "ℹ️ Информация",
        "💰 Начать подсчет основных работ",
        "💰 Начать подсчет дополнительных работ",
        "📊 Итог за месяц",
        "⏳ Итог за все время",
        '📋 Показать все доп. работы'
    ]
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])

    bot.send_message(message.chat.id, "Добро пожаловать! Выберите действие:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "ℹ️ Информация")
def info(message):
    text = (
        "📌 Этот бот помогает учитывать выполненные работы и зарплату\n\n"
        "🔹 Для добавления работы нажмите '💰 Начать подсчет'\n"
        "🔹 Просмотр текущего месяца - '📊 Итог за месяц'\n"
        "🔹 Общая статистика - '⏳ Итог за все время'\n\n"
        "Данные сохраняются автоматически!"
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda message: message.text == "💰 Начать подсчет основных работ")
def start_calculation(message):
    user_id = message.from_user.id
    user_states[user_id] = WORK_MENU

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["➕ Добавить работу", "💾 Сохранить месяц", "🔙 Назад"]
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])

    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "💰 Начать подсчет дополнительных работ")
def start_calculation_paid_works(message):
    user_id = message.from_user.id
    user_states[user_id] = PAID_WORK_MENU

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Добавляем новые кнопки в меню
    buttons = [
        "➕ Добавить дополнительную работу",
        "🗑️ Удалить последнюю доп. работу",
        "📋 Показать все доп. работы",
        "🔙 Назад"
    ]
    markup.add(types.KeyboardButton(buttons[0]))
    markup.add(types.KeyboardButton(buttons[1]), types.KeyboardButton(buttons[2]))
    markup.add(types.KeyboardButton(buttons[3]))

    bot.send_message(message.chat.id, "Выберите действие в меню доп. работ:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "➕ Добавить дополнительную работу")
def add_paid_work_menu(message):
    user_id = message.from_user.id
    user_states[user_id] = ADD_PAID_WORK_MENU

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(types.KeyboardButton("🔙 Назад"))
    msg = bot.send_message(message.chat.id, "🔢 Введите **номер работы**:", reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_number_step)


def process_number_step(message):
    user_id = message.from_user.id

    if message.text == "🔙 Назад":
        user_states[user_id] = PAID_WORK_MENU
        start_calculation_paid_works(message)
        return

    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]['number'] = message.text.strip()

    msg = bot.send_message(message.chat.id, "💰 Теперь введите **сумму** (грязную, до расчета КП):",
                           parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_amount_step)


def process_amount_step(message):
    user_id = message.from_user.id

    if message.text == "🔙 Назад":
        user_states[user_id] = PAID_WORK_MENU
        start_calculation_paid_works(message)
        return

    amount_text = message.text.strip()

    if not amount_text.isdigit():
        msg = bot.send_message(message.chat.id, "❌ Ошибка! Введите сумму целым числом без букв и знаков:")
        bot.register_next_step_handler(msg, process_amount_step)
        return

    number = user_data.get(user_id, {}).get('number')
    if not number:
        bot.send_message(message.chat.id, "❌ Произошла ошибка (потерялись данные номера). Начните сначала.")
        user_states[user_id] = PAID_WORK_MENU
        start_calculation_paid_works(message)
        return

    calculated_price = add_paid_work(user_id, number, amount_text)

    bot.send_message(
        message.chat.id,
        f"✅ Дополнительная работа добавлена!\n"
        f"🔢 Номер: `{number}`\n"
        f"💰 Чистый расчет КП: {calculated_price} руб.",
        parse_mode="Markdown"
    )

    user_data[user_id].pop('number', None)
    user_states[user_id] = PAID_WORK_MENU
    start_calculation_paid_works(message)


@bot.message_handler(func=lambda message: message.text == '🗑️ Удалить последнюю доп. работу')
def delete_last_paid_work(message):
    user_id = message.from_user.id
    number, price = db_delete_last_paid_work(user_id)

    if number:
        response = f"❌ Удалена доп. работа:\n🔢 Номер: `{number}`\n💰 Цена: {price} руб."
    else:
        response = "❌ Нечего удалять. Список дополнительных работ пуст."

    bot.send_message(message.chat.id, response, parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text == '📋 Показать все доп. работы')
def show_all_paid_works(message):
    user_id = message.from_user.id
    works = get_all_paid_works(user_id)

    if not works:
        bot.send_message(message.chat.id, "📋 У вас пока нет записанных дополнительных работ.")
        return

    response = "📋 **Список всех ваших дополнительных работ:**\n\n"
    total_paid_sum = 0

    for row in works:
        number, price, date_str = row
        total_paid_sum += price

        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            formatted_date = dt.strftime("%d.%m.%Y %H:%M")
        except Exception:
            formatted_date = date_str

        response += f"🔹 №`{number}` — {price} руб. _({formatted_date})_\n"

    response += f"\n💵 **Итого за все доп. работы:** {round(total_paid_sum, 2)} руб."

    bot.send_message(message.chat.id, response, parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text == "➕ Добавить работу")
def add_work_menu(message):
    user_id = message.from_user.id
    user_states[user_id] = ADD_WORK_MENU

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttons = list(WORKS.keys()) + ['🗑️ Удалить последнюю работу', "🔙 Назад"]
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])

    bot.send_message(message.chat.id, "Выберите выполненную работу:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '🗑️ Удалить последнюю работу')
def delete_last_work(message):
    user_id = message.from_user.id
    work_type, price = db_delete_last_work(user_id)

    if work_type:
        response = (
            f"❌ Удалено: {work_type} - {price} руб."
        )
    else:
        response = "❌ Нечего удалять"

    bot.send_message(message.chat.id, response)


@bot.message_handler(
    func=lambda message: user_states.get(message.from_user.id) == ADD_WORK_MENU and message.text in WORKS)
def process_work(message):
    user_id = message.from_user.id
    work_type = message.text
    price = add_work(user_id, work_type)

    month_total = get_month_total(user_id)
    all_time_total = get_all_time_total(user_id)

    response = (
        f"✅ Добавлено: {work_type} - {price} руб.\n"
        f"📅 Текущий месяц: {month_total} руб.\n"
        f"⏳ Всего: {all_time_total} руб."
    )
    bot.send_message(message.chat.id, response)


@bot.message_handler(func=lambda message: message.text == "💾 Сохранить месяц")
def process_save_month(message):
    user_id = message.from_user.id
    saved_amount = save_month(user_id)

    if saved_amount > 0:
        response = (
            f"💾 Месяц сохранен!\n"
            f"Сохраненная сумма: {saved_amount} руб.\n"
            f"Теперь можно начать новый месяц."
        )
    else:
        response = "Нет данных для сохранения за текущий месяц."

    bot.send_message(message.chat.id, response)


@bot.message_handler(func=lambda message: message.text == "📊 Итог за месяц")
def show_month_total(message):
    user_id = message.from_user.id
    total = get_month_total(user_id)
    bot.send_message(message.chat.id, f"📊 Итог за текущий месяц: {total} руб.")


@bot.message_handler(func=lambda message: message.text == "⏳ Итог за все время")
def show_all_time_total(message):
    user_id = message.from_user.id
    total = get_all_time_total(user_id)
    bot.send_message(message.chat.id, f"⏳ Общий итог за все время: {total} руб.")


@bot.message_handler(func=lambda message: message.text == "🔙 Назад")
def back_handler(message):
    user_id = message.from_user.id
    current_state = user_states.get(user_id, MAIN_MENU)

    if current_state == ADD_WORK_MENU:
        user_states[user_id] = WORK_MENU
        start_calculation(message)
    elif current_state == WORK_MENU:
        user_states[user_id] = MAIN_MENU
        start(message)
    elif current_state == ADD_PAID_WORK_MENU:
        user_states[user_id] = PAID_WORK_MENU
        start_calculation_paid_works(message)
    elif current_state == PAID_WORK_MENU:
        user_states[user_id] = MAIN_MENU
        start(message)
    else:
        start(message)


@bot.message_handler(commands=['cleardb'])
def clear_database(message):
    if message.from_user.id == id_admin:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM works")
        cursor.execute("DELETE FROM monthly_totals")
        cursor.execute("DELETE FROM users")

        conn.commit()
        conn.close()

        bot.reply_to(message, "✅ База данных полностью очищена!")
    else:
        bot.reply_to(message, "⛔ У вас нет прав для выполнения этой команды")
