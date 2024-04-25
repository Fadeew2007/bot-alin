import asyncio
import aiohttp
from bs4 import BeautifulSoup
from telegram.ext import Application
import time
import os
from aiohttp import web

async def fetch_prices(session, url, indices):
    async with session.get(url) as response:
        content = await response.text()
        soup = BeautifulSoup(content, 'html.parser')
        product_name = soup.find('h1').text.strip()
        price_elements = soup.find_all(class_='cat-price-value')
        prices = [price_elements[i].text.strip().replace('\n', ' і не цікава ціна ') for i in indices if i < len(price_elements)]
        return product_name, prices

async def track_price_changes(token, chat_id, url, indices, start_delay, check_interval=86400):
    await asyncio.sleep(start_delay)
    app = Application.builder().token(token).build()
    async with aiohttp.ClientSession() as session:
        last_prices = None
        while True:
            try:
                product_name, current_prices = await fetch_prices(session, url, indices)
                if last_prices is not None:
                    for i, (last_price, current_price) in enumerate(zip(last_prices, current_prices)):
                        if last_price != current_price:
                            message = f'Ціна {i+1} на "{product_name}" змінилася з {last_price} на {current_price}'
                            await app.bot.send_message(chat_id, text=message)
                last_prices = current_prices
                print(f'Перевірено на {time.ctime()}: {product_name} - ціни {current_prices}')
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
        {"url": "https://ukr-prokat.com/orenda-avto/ravon-r2-shevrolet-spark.html", "indices": [1, 2, 3, 4], "delay": 0},
        {"url": "https://ukr-prokat.com/orenda-avto/hyundai-accent.html", "indices": [1, 2, 3, 4], "delay": 10},
        {"url": "https://ukr-prokat.com/orenda-avto/suzuki-vitara.html", "indices": [1, 2, 3, 4], "delay": 20},
        {"url": "https://ukr-prokat.com/orenda-avto/kia-sportage-2019-2.html", "indices": [1, 2, 3, 4], "delay": 30},
        {"url": "https://ukr-prokat.com/orenda-avto/toyota-rav4.html", "indices": [1, 2, 3, 4], "delay": 40},
    ]

    tasks = [start_server()]
    for product in products:
        task = track_price_changes(TOKEN, CHAT_ID, product['url'], product['indices'], product['delay'])
        tasks.append(task)
    
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
