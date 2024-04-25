import asyncio
import aiohttp
from bs4 import BeautifulSoup
from telegram.ext import Application
import time
import os
from aiohttp import web

async def fetch_price_and_name(session, url):
    async with session.get(url) as response:
        content = await response.text()
        soup = BeautifulSoup(content, 'html.parser')
        product_name = soup.find('h1').text.strip()
        price_elements = soup.find_all(class_='block px-6 py-2')
        price = price_elements[4].text.strip()
        return product_name, price

async def track_price_changes(token, chat_id, url, start_delay, check_interval=30):
    await asyncio.sleep(start_delay)
    app = Application.builder().token(token).build()
    async with aiohttp.ClientSession() as session:
        last_price = None
        while True:
            try:
                product_name, current_price = await fetch_price_and_name(session, url)
                if last_price is not None and current_price != last_price:
                    message = f'Ціна на "{product_name}" змінилася з {last_price} на {current_price}'
                    await app.bot.send_message(chat_id, text=message)
                last_price = current_price
                print(f'Перевірено на {time.ctime()}: {product_name} - ціна {current_price}')
            except Exception as e:
                print(f'Помилка під час виконання скрипта: {e}')
            await asyncio.sleep(check_interval)

async def start_server():
    app = web.Application()
    app.router.add_get('/', lambda request: web.Response(text="Server is running"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 80)
    await site.start()

async def main():
    TOKEN = '7081365803:AAG0I20iXpdo3vDOJ_PsndeEslZzYwuUwcM'
    CHAT_ID = '530420753'
    products = [
        {"url": "https://alin.ua/info-car/ford-fiesta-hatchback-lviv", "delay": 0},
        {"url": "https://alin.ua/info-car/ravon-r2", "delay": 10},
    ]

    tasks = [start_server()]
    for product in products:
        task = track_price_changes(TOKEN, CHAT_ID, product['url'], product['delay'])
        tasks.append(task)
    
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())