from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from datetime import datetime, timedelta
import requests

from database import Database
from keyboard import generate_lang_button, generate_period_button
from langs import langs


bot = Bot(token='')
dp = Dispatcher(bot)
db = Database()
city = None


@dp.message_handler(commands=['start'])
async def command_start(message: Message):
    chat_id = message.chat.id
    db.create_users_table()
    await bot.send_message(chat_id, 'Select language\nВыберите язык', reply_markup=generate_lang_button())


@dp.message_handler(regexp='🇺🇸 English|🇷🇺 Русский')
async def get_lang_register_user(message: Message):
    chat_id = message.chat.id
    lang = message.text
    name = message.from_user.full_name
    if lang == '🇺🇸 English':
        lang = 'en'
    else:
        lang = 'ru'
    user = db.get_user_by_chat_id(chat_id)
    if user:
        db.set_user_language(chat_id, lang)
    else:
        db.first_register_user(chat_id, name)
        db.set_user_language(chat_id, lang)
    await message.answer(langs[lang]['lang'], reply_markup=ReplyKeyboardRemove())


@dp.message_handler(commands=['help'])
async def command_help(message: Message):
    chat_id = message.chat.id
    lang = db.get_user_language(chat_id)
    await message.answer(langs[lang]['help'])


@dp.message_handler(commands=['set_city'])
async def get_city(message: Message):
    chat_id = message.chat.id
    lang = db.get_user_language(chat_id)
    await bot.send_message(chat_id, langs[lang]['city'])


@dp.message_handler(lambda message: db.get_user_language(message.chat.id) and message.text and not message.text.startswith('/'))
async def ask_period(message: Message):
    chat_id = message.chat.id
    lang = db.get_user_language(chat_id)
    global city
    city = message.text
    await bot.send_message(chat_id, langs[lang]['time'], reply_markup=generate_period_button(lang))


@dp.callback_query_handler(lambda call: call.data in ['today', 'three_days'])
async def get_data(callback: CallbackQuery):
    db.create_weather_table()
    chat_id = callback.from_user.id
    lang = db.get_user_language(chat_id)
    await callback.answer(langs[lang]['period'])
    if not lang or lang not in langs:
        lang = 'en'
    global city

    if not city:
        await bot.send_message(chat_id, langs[lang]['error'])
        return

    if callback.data == 'today':
        dt = datetime.now()
        days = 1
    else:
        dt = datetime.now()
        days = 4

    params = {
        'q': city,
        'appid': '',
        'units': 'metric',
        'lang': lang,
        'dt': int(dt.timestamp())
    }
    try:
        response = requests.get('https://api.openweathermap.org/data/2.5/forecast', params=params).json()
        data = response['list']
        for i in range(days):
            for dat in data:
                if dat['dt_txt'].startswith((dt + timedelta(days=i)).strftime('%Y-%m-%d')):
                    temp = dat['main']['temp']
                    description = dat['weather'][0]['description']
                    humidity = dat['main']['humidity']
                    pressure = dat['main']['pressure']
                    wind_speed = dat['wind']['speed']
                    if lang == 'en':
                        await callback.message.answer(
                            f"In {city}, on {(dt + timedelta(days=i)).strftime('%Y-%m-%d')}\n"
                            f"Temperature: {temp} C\n"
                            f"Description: {description}\n"
                            f"Humidity: {humidity} %\n"
                            f"Pressure: {pressure} hPa\n"
                            f"Wind Speed: {wind_speed} m\s")
                    else:
                        await callback.message.answer(
                            f"В {city}, на {(dt + timedelta(days=i)).strftime('%Y-%m-%d')}\n"
                            f"Температура: {temp} С\n"
                            f"Описание: {description}\n"
                            f"Влажность: {humidity} %\n"
                            f"Давление: {pressure} hPa\n"
                            f"Скорость ветра: {wind_speed} м\с")
                    db.insert_data(city, temp, description, humidity, pressure, wind_speed, chat_id)
                    break
    except Exception as e:
        await callback.message.answer(f"{langs[lang]['error']}")


@dp.message_handler(commands=['history'])
async def command_history(message: Message):
    chat_id = message.chat.id
    lang = db.get_user_language(chat_id)
    history = db.get_history(chat_id)
    history_message = ""
    for item in history:
        if isinstance(item, tuple):
            if lang == 'en':
                history_message += f'In the city {item[1]}: Temperature: {item[2]} С, Condition: {item[3]}\n'
            else:
                history_message += f'В городе {item[1]}: Температура: {item[2]} С, Состояние: {item[3]}\n'
        else:
            history_message += f"{item}\n"
    await bot.send_message(chat_id, f"{langs[lang]['history']}\n{history_message}")

executor.start_polling(dp)
