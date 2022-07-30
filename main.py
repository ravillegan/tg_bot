from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.executor import start_webhook
import motor.motor_asyncio
from datetime import datetime
import random
import logging
import os

TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

users = {}
in_day_ochko = {}

async def add_user(chat_id, user_id):
    if chat_id in list(users.keys()):
        if user_id in list(users[chat_id].keys()):
            return 'already'
    if chat_id not in list(users.keys()):
        users[chat_id] = {user_id: 0}
        return 'new'
    users[chat_id][user_id] = 0
    return 'new'

async def update_user(chat_id, user_id):
    users[chat_id][user_id] += 1

async def random_user(chat_id):
    if chat_id not in list(users.keys()):
        return 'no_one'
    tmp = list(users[chat_id].keys())
    random.shuffle(tmp)
    login = tmp[0]
    return login

async def set_ochko_day(chat_id, login):
    if chat_id not in in_day_ochko:
        in_day_ochko[chat_id] = [datetime.now().date(), login]
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
    list_of_tuples = list(users[chat_id].items())
    new_tuple = await Sort_Tuple(list_of_tuples)
    print(new_tuple)
    stats_str = ''
    for i in range(len(new_tuple)):
        stats_str += str(i+1)+ '. '+new_tuple[i][0]
        stats_str += ': '
        stats_str += str(new_tuple[i][1])
        stats_str += '\n'
    return stats_str




#start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.chat.id, 'Ну и зря вы это начали... Ну ладно, поиграем в очкошника')

#reg
@dp.message_handler(commands=['reg'])
async def start(message: types.Message):
    status = await add_user(message.chat.id, message.from_user.username)
    if status == 'already':
        await bot.send_message(message.chat.id, 'Так ты же уже играешь')
    else:
        await bot.send_message(message.chat.id, 'Ох. Ты вступил на скользкий путь, ну ладно, ты в игре')

#kto
@dp.message_handler(commands=['kto'])
async def start(message: types.Message):
    login = await random_user(message.chat.id)
    if login == 'no_one':
        await bot.send_message(message.chat.id, 'Никто из вас еще не играет(( Хочешь играть - зарегайся /reg')
    else:
        login, new_old = await set_ochko_day(message.chat.id, login)
        if new_old == 'already':
            await bot.send_message(message.chat.id, 'Сегодня же уже выясняли... очкошник дня - @'+login)
        else:
            await bot.send_message(message.chat.id, 'Зряяя. Ну ладно')
            await bot.send_message(message.chat.id, 'Очкошник дня - @'+login)
            await update_user(message.chat.id, login)

#reg
@dp.message_handler(commands=['stats'])
async def start(message: types.Message):
    status_stats = await statistics(message.chat.id)
    if status_stats == 'no_chat_id':
        await bot.send_message(message.chat.id, 'Ни одной игры не было')
    else:
        await bot.send_message(message.chat.id, 'Топ очкошников: \n \n'+ status_stats)


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

executor.start_polling(dp)