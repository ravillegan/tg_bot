from operator import length_hint
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.executor import start_webhook
import motor.motor_asyncio
from datetime import datetime
import random
import logging
import os
from random import randint
import pprint

TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

cluster = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://raville_ganiev:07089910Rgu@cluster0.5giudi4.mongodb.net/?retryWrites=true&w=majority")
users_collection = cluster.ochkoshniki.ochkoshniki_users
day_ochko_collection = cluster.ochkoshniki.ochkoshniki_day_status

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')


async def add_user(chat_id, user_id, user_name):
    if await users_collection.count_documents({'chat_id': {'$eq': str(chat_id)}, 'user_id': {'$eq': str(user_id)}}) != 0:
        return 'already'
    if await users_collection.count_documents({'chat_id': {'$eq': str(chat_id)}}) == 0:
        await users_collection.insert_one({'chat_id': str(chat_id), 'user_id': str(user_id), 'user_name' : user_name, 'score': 0})
        return 'new'
    await users_collection.insert_one({'chat_id': str(chat_id), 'user_id': str(user_id), 'user_name' : user_name, 'score': 0})
    # print(users_collection)
    return 'new'

async def update_user(chat_id, user_id):
    info = await users_collection.find_one({'chat_id': str(chat_id), 'user_id': str(user_id)})
    new_score = info.score + 1
    # print(users_collection, new_score)

async def random_user(chat_id):
    if await users_collection.count_documents({'chat_id': {'$eq': str(chat_id)}}) == 0:
        return 'no_one'
    cursor = await users_collection.find({'chat_id': {'$eq': str(chat_id)}})
    print(cursor)
    tmp = []
    for document in await cursor.to_list(length=1000):
        tmp.append(document.user_name)
    random.shuffle(tmp)
    user_id = tmp[0]
    return user_id


async def set_ochko_day(chat_id, user_id):
    if await day_ochko_collection.count_documents({'chat_id': {'$eq': str(chat_id)}}) == 0:
        await day_ochko_collection.insert_one({'chat_id': str(chat_id), 'date': str(datetime.now().date()), 'user_name' : user_id})
        return user_id, 'new'
    if await users_collection.find({'chat_id': {'$eq': str(chat_id)}}).date == str(datetime.now().date()):
        user_id = await users_collection.find({'user_id': {'$eq': str(user_id)}}).date
        return user_id, 'already'
    await day_ochko_collection.update_one({'chat_id': str(chat_id), 'user_name' : user_id}, {'$set': {'date': str(datetime.now().date())}})
    return user_id, 'new'

async def Sort_Tuple(tup):
    tup.sort(key = lambda x: x[1], reverse=True)
    return tup

async def statistics(chat_id):
    if await users_collection.count_documents({'chat_id': {'$eq': str(chat_id)}}) == 0:
        return 'no_chat_id'
    stats_str = []
    cursor = users_collection.find({'chat_id': str(chat_id)}).sort('score', -1)
    # cursor1 = users_collection.find()
    # print(cursor, cursor1, 'blyat', str(chat_id), users_collection.count_documents({'chat_id': {'$eq': str(chat_id)}}))
    i = 0
    async for document in await cursor.to_list(length=1000):
        stats_str += str(i+1)+ '. '+document.user_name
        stats_str += ': '
        stats_str += document.score
        stats_str += '\n'
        i+=1
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
    status = await add_user(message.chat.id, message.from_user.id, user_name)
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
        user_name = await users_collection.find({'chat_id': {'$eq': str(message.chat.id)}, 'user_id': {'$eq': str(user_id)}}).date
        if new_old == 'already':
            rand_reg = randint(0, 3)
            if rand_reg == 0:
                await bot.send_message(message.chat.id, 'Читать не умеешь? Я же сегодня писал уже.')
            if rand_reg == 1:
                await bot.send_message(message.chat.id, 'Сегодня же уже выясняли... очкошник дня - @'+user_name)
            if rand_reg == 2:
                await bot.send_message(message.chat.id, 'Ну епта, выяснили же уже, что за очкошничество сегодня отвечает @'+user_name)
            if rand_reg == 3:
                await bot.send_message(message.chat.id, 'Мне не впадлу, я еще раз могу написать, что сегодняшний очкошник - @'+user_name)
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
            await bot.send_message(message.chat.id, 'очкошник дня - @'+user_name)
            await update_user(message.chat.id, user_id, user_name)

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