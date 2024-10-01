import telebot
from telebot import types
import random

bot = telebot.TeleBot("-)
print(f"🤖 Бот запустился, проверяйте телегу!")

# Словарь для уровней и количества стаканчиков
levels = {
    "🎲 Уровень 'Тест' (2 стакана)": (2, "🥤🥤"),
    "🔮 Уровень 'Хорошая интуиция' (3 стакана)": (3, "🥤🥤🥤"),
    "🧙‍♂️ Уровень 'Сильная интуиция!' (5 стаканов)": (5, "🥤🥤🥤🥤🥤"),
    "👑 Уровень 'GOD!' (10 стаканов)": (10, "🥤🥤🥤🥤🥤🥤🥤🥤🥤🥤"),
}

# Счетчики
scores = {}
failures = {}
user_levels = {}
attempts = {}
secret_cups = {}

# Функция для начала игры
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🔔 Вы всегда можете остановить игру командой /stop")
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for level in levels:
        markup.add(types.KeyboardButton(level))
    bot.send_message(message.chat.id, "👋 Привет! Давай сыграем в игру 'Угадай под каким стаканом шарик!' 🤔\n"
                                      "Выберите уровень:", reply_markup=markup)

# Функция для выбора уровня игры
@bot.message_handler(func=lambda message: message.text in levels.keys())
def choose_level(message):
    level = message.text
    user_levels[message.from_user.id] = level
    num_cups, cups = levels[level]

    # Генерация секретного стакана
    secret_cup = random.randint(1, num_cups)
    secret_cups[message.from_user.id] = secret_cup
    bot.send_message(message.chat.id, f"🎩 Отлично! Я спрятал шарик под одним из этих стаканчиков:\n{cups}")
    send_cups_buttons(message.chat.id, num_cups)

# Функция для отправки кнопок со стаканчиками
def send_cups_buttons(chat_id, num_cups):
    markup = types.InlineKeyboardMarkup(row_width=5)  # До 5 кнопок в ряд
    buttons = []
    for i in range(1, num_cups + 1):
        buttons.append(types.InlineKeyboardButton("🥤", callback_data=str(i)))

    # Разбиваем кнопки на ряды по 5 стаканчиков
    markup.add(*buttons)
    bot.send_message(chat_id, "Выберите стаканчик:", reply_markup=markup)

# Обработчик выбора стаканчика
@bot.callback_query_handler(func=lambda call: True)
def callback_guess_number(call):
    user_id = call.from_user.id
    guessed_cup = int(call.data)
    secret_cup = secret_cups.get(user_id)  # Получаем секретный стакан

    attempts[user_id] = attempts.get(user_id, 0) + 1

    if guessed_cup == secret_cup:
        bot.send_message(call.message.chat.id, f"🎉 Поздравляю! Вы угадали, шарик был под стаканчиком {guessed_cup}!")
        scores[user_id] = scores.get(user_id, 0) + 1

        if scores[user_id] >= 3:
            bot.send_message(call.message.chat.id, f"🏆 Вы выиграли! 🎯\n"
                                                   f"Количество попыток: {attempts[user_id]} ⚙️\n"
                                                   f"Неудачных: {failures.get(user_id, 0)} 😓")
            reset_game(user_id)
            send_stop_button(call.message.chat.id)
        else:
            bot.send_message(call.message.chat.id, "🎲 Давайте сыграем еще раз!")
            next_round(call.message, user_id)
    else:
        bot.send_message(call.message.chat.id, f"🙈 Мимо! Попробуйте снова.")
        failures[user_id] = failures.get(user_id, 0) + 1
        next_round(call.message, user_id)

# Функция для нового раунда
def next_round(message, user_id):
    level = user_levels.get(user_id)
    num_cups, cups = levels[level]
    secret_cup = random.randint(1, num_cups)
    secret_cups[user_id] = secret_cup

    bot.send_message(message.chat.id, f"🤫 Я снова спрятал шарик под одним из этих стаканчиков:\n{cups}")
    send_cups_buttons(message.chat.id, num_cups)

# Функция для сброса игры
def reset_game(user_id):
    scores[user_id] = 0
    failures[user_id] = 0
    user_levels.pop(user_id, None)
    attempts.pop(user_id, None)
    secret_cups.pop(user_id, None)

# Функция для отправки кнопки /stop
def send_stop_button(chat_id):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(chat_id, "🚫 Игра остановлена. Введите команду /start для начала новой игры.", reply_markup=markup)

# Обработчик команды /stop
@bot.message_handler(commands=['stop'])
def stop_game(message):
    send_stop_button(message.chat.id)

import time
while True:
    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"Смотри: {e}")
        time.sleep(5)
