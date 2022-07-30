from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.executor import start_webhook
import motor.motor_asyncio
from datetime import datetime
import random
import logging
import os
from random import randint

TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

users = {}
in_day_ochko = {}

async def add_user(chat_id, user_id, user_name):
    if chat_id in list(users.keys()):
        if user_id in list(users[chat_id].keys()):
            return 'already'
    if chat_id not in list(users.keys()):
        users[chat_id] = {user_id: {user_name: 0}}
        return 'new'
    users[chat_id][user_id][user_name] = 0
    return 'new'

async def update_user(chat_id, user_id):
    users[chat_id][user_id]['user_name'] += 1

async def random_user(chat_id):
    if chat_id not in list(users.keys()):
        return 'no_one'
    tmp = list(users[chat_id].keys())
    random.shuffle(tmp)
    user_id = tmp[0]
    return user_id


async def set_ochko_day(chat_id, user_id):
    if chat_id not in in_day_ochko:
        in_day_ochko[chat_id] = [datetime.now().date(), user_id]
        return in_day_ochko[chat_id][1], 'new'
    if in_day_ochko[chat_id][0] == datetime.now().date():
        return in_day_ochko[chat_id][1], 'already'
    return in_day_ochko[chat_id][1], 'new'

async def Sort_Tuple(tup):
    tup.sort(key = lambda x: x[1], reverse=True)
    return tup

async def statistics(chat_id):
    if chat_id not in list(users.keys()):
        return 'no_chat_id'
    array = []
    list_of_tuples = list(users[chat_id].items())
    print(list_of_tuples)
    for i in range(len(list_of_tuples)):
        array.append(list(list_of_tuples[i][1].items()))
    flat_list = [item for sublist in array for item in sublist]
    print(flat_list)
    new_tuple = Sort_Tuple(flat_list)
    print(new_tuple)
    stats_str = ''
    for i in range(len(new_tuple)):
        stats_str += str(i+1)+ '. '+new_tuple[i][0]
        stats_str += ': '
        stats_str += str(new_tuple[i][1])
        stats_str += '\n'
    return stats_str

async def user_info(user_info_json):
    if hasattr(user_info_json, 'username') and user_info_json.username is not None:
        user_id = user_info_json.username
    elif hasattr(user_info_json, 'first_name') and hasattr(user_info_json, 'last_name') and user_info_json.first_name is not None and user_info_json.last_name is not None:
        user_id = user_info_json.first_name + ' ' + user_info_json.last_name
    elif hasattr(user_info_json, 'last_name') and user_info_json.last_name is not None:
        user_id = user_info_json.last_name
    elif hasattr(user_info_json, 'first_name') and user_info_json.first_name is not None:
        user_id = user_info_json.first_name
    else:
        user_id ='Таинственный очкошник ' +user_info_json.from_user.id
    return user_id



#start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.chat.id, 'Ну и зря вы это начали... Ну ладно, поиграем в очкошника')

#reg
@dp.message_handler(commands=['reg'])
async def start(message: types.Message):
    user_name = await user_info(message.from_user)
    status = await add_user(message.chat.id, user_name)
    if status == 'already':
        await bot.send_message(message.chat.id, 'Так ты же уже играешь')
    else:
        rand_reg = randint(0, 3)
        if rand_reg == 0:
            await bot.send_message(message.chat.id, 'Подумой не играй! Хотя ладно, твой выбор')
        if rand_reg == 1:
            await bot.send_message(message.chat.id, 'Ох. Ты ступил на скользкий путь, ну ладно, ты в игре')
        if rand_reg == 2:
            await bot.send_message(message.chat.id, 'Ты играешь с огнем, но мне пох, играй')
        if rand_reg == 3:
            await bot.send_message(message.chat.id, 'Обратного пути не будет, ты по любому станешь очкошником')

#kto
@dp.message_handler(commands=['kto'])
async def start(message: types.Message):
    user_id = await random_user(message.chat.id)
    if user_id == 'no_one':
        await bot.send_message(message.chat.id, 'Никто из вас еще не играет(( Хочешь играть - зарегайся /reg')
    else:
        user_id, new_old = await set_ochko_day(message.chat.id, user_id)
        if new_old == 'already':
            rand_reg = randint(0, 3)
            if rand_reg == 0:
                await bot.send_message(message.chat.id, 'Читать не умеешь? Я же сегодня писал уже.')
            if rand_reg == 1:
                await bot.send_message(message.chat.id, 'Сегодня же уже выясняли... очкошник дня - @'+list(users[message.chat.id][user_id].keys())[0])
            if rand_reg == 2:
                await bot.send_message(message.chat.id, 'Ну епта, выяснили же уже, что за очкошничество сегодня отвечает @'+list(users[message.chat.id][user_id].keys())[0])
            if rand_reg == 3:
                await bot.send_message(message.chat.id, 'Мне не впадлу, я еще раз могу написать, что сегодняшний очкошник - @'+list(users[message.chat.id][user_id].keys())[0])
        else:
            if message.from_user.id == user_id:
                await bot.send_message(message.chat.id, 'Ты зачем спрашиваешь? Ты и есть очкошник сегодня')
            else:
                rand = randint(0, 3)
                if rand == 0:
                    await bot.send_message(message.chat.id, 'Делать нечего?. Ну ладно, щас выясним')
                if rand == 1:
                    await bot.send_message(message.chat.id, 'Ууу съука. Пахнет очкошничеством, а значит...')
                if rand == 2:
                    await bot.send_message(message.chat.id, 'Падажжи. Так, очкошник кто?')
                if rand == 3:
                    await bot.send_message(message.chat.id, 'Ща проанализирую. Логарифм хуе мое, делим... ага')
            await bot.send_message(message.chat.id, 'очкошник дня - @'+list(users[message.chat.id][user_id].keys())[0])
            await update_user(message.chat.id, list(users[message.chat.id][user_id].keys())[0])

#stats
@dp.message_handler(commands=['stats'])
async def start(message: types.Message):
    status_stats = await statistics(message.chat.id)
    if status_stats == 'no_chat_id':
        await bot.send_message(message.chat.id, 'Ни одной игры не было')
    else:
        await bot.send_message(message.chat.id, 'Топ очкошников: \n \n'+ status_stats)

#secret
@dp.message_handler(commands=['secret'])
async def start(message: types.Message):
    await bot.send_message(message.chat.id, message.from_user)


# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)

async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)

async def on_shutdown(dispatcher):
    await bot.delete_webhook()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )

# executor.start_polling(dp)