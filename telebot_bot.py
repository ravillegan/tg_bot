import telebot
import random
import os, sys
from requests.exceptions import ConnectionError, ReadTimeout

# Создаем экземпляр бота
bot = telebot.TeleBot('5470935385:AAGASEKHUuVewTHaY2V6Z0c7ARjKorQBO7Y')

users = {'Искандер': 500}

def add_user(nickname):
    users[nickname] = 0

def increase_score(nickname):
    users[nickname] += 1

# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Ну что, определим, кто очкошник? Нажми /kto_ochkoshnik')

# # Функция, обрабатывающая команду /reg
# @bot.message_handler(commands=["reg"])
# def kto_ochkoshnik(m, res=False):
#     bot.send_message(m.chat.id, 'Ох, ты вступил на скользкий путь очкошничества')
#     add_user(m.from_user.username)

# # Функция, обрабатывающая команду /stats
# @bot.message_handler(commands=["stats"])
# def kto_ochkoshnik(m, res=False):
#     bot.send_message(m.chat.id, list(users.items())[0])

# Функция, обрабатывающая команду /kto_ochkoshnik
@bot.message_handler(commands=["kto_ochkoshnik"])
def kto_ochkoshnik(m, res=False):
    bot.send_message(m.chat.id, 'Очкошник уже не Искандер, а Шалва')
    # increase_score(m.from_user.username)


# # Получение сообщений от юзера
# @bot.message_handler(content_types=["text"])
# def handle_text(message):
#     bot.send_message(message.chat.id, 'Походу ты и есть очкошник, раз пишешь "'+message.text+'"')
# Запускаем бота

bot.polling(none_stop=True)