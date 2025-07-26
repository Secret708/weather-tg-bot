import asyncio
import aiohttp
import os

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from dotenv import load_dotenv
from datetime import datetime

load_dotenv('TOKEN.env') # загружает документ .env с токеном бота и API_KEY
TOKEN = os.getenv('TOKEN_BOT') # извлекает токен
API_KEY = os.getenv('API_KEY_WEATHER') # извлекает API_KEY

if not TOKEN: # проверка есть ли токен. Можно взять у @BotFather
    raise ValueError('not TOKEN')

if not API_KEY: # проверка есть ли API_KEY от OpenWeatherMap
    raise ValueError('not API_KEY')

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def get_weather(message: Message, city, api_key=API_KEY): # возвращает .json документ с параметрами погоды
    try:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={str(api_key)}&units=metric'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    await message.answer(f'Ошибка запроса: {response.status}')
    except Exception as e:
        print(f'Ошибка {e}')

@dp.message(lambda message: message.text == '/start') # выводит приветственную фразу
async def start(message: Message):
    await message.answer('Привет, я бот для того чтобы узнать погоду. Чтобы узнать погоду напиши /weather <город>')

@dp.message(lambda message: message.text.startswith('/weather')) # выводит информацию о погоде
async def weather(message: Message):
    parts = message.text.split()

    if len(parts) > 1:
        try:
            city = " ".join(parts[1:])

            weather_data = await get_weather(message, city)

            await message.answer(f"""Погода в {weather_data['name']}, {weather_data['sys']['country']}\n
<b>Температура</b>: {weather_data['main']['temp']}°C
<b>Ощущается как:</b> {weather_data['main']['feels_like']}°C
<b>Влажность</b>: {weather_data['main']['humidity']}%
<b>Давление</b>: {weather_data['main']['pressure']}hPa
<b>Скорость ветра</b>: {weather_data['wind']['speed']}м/с
<b>Описание</b>: {weather_data['weather'][0]['description']}
<b>Восход</b>: {datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M:%S')}
<b>Закат</b>: {datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M:%S')}""",
                                 parse_mode="HTML")
        except Exception as e:
            print(f'Ошибка {e}')
    else:
        await message.answer('Введены не все данные')

async def main(): # главный цикл бота
    while True:
        try:
            print('Запуск бота')
            await dp.start_polling(bot)
        except Exception as e:
            print(f'Ошибка {e}')
            print('Перезапуск бота')
            await asyncio.sleep(3)

if __name__ == '__main__':
    asyncio.run(main())