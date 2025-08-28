import ipaddress
import json
import logging

import aioredis
from flask import Flask, request

logging.basicConfig(
    level=logging.INFO,
    format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    filename='flask_web.log'
)

app = Flask(__name__)
IPS = [
    ipaddress.IPv4Network('185.71.76.0/27'),
    ipaddress.IPv4Network('185.71.77.0/27'),
    ipaddress.IPv4Network('77.75.153.0/25'),
    ipaddress.IPv4Network('77.75.156.11'),
    ipaddress.IPv4Network('77.75.156.35'),
    ipaddress.IPv4Network('77.75.154.128/25'),
    ipaddress.IPv6Network('2a02:5180::/32'),
    ipaddress.IPv4Network('127.0.0.1'),
]


@app.route('/payments/classic', methods=['POST'])  # https://meditationinfo.exnet.su/payments/classic
async def cb_handler():
    ip = ipaddress.ip_address(request.remote_addr)
    # logging.info(f"{ip=}\n")

    if not any(ip in ip_range for ip_range in IPS):  # Проверка на IP адрес от Юкассы
        return "Ошибка: доступ запрещен.", 403

    data = request.get_json()
    logging.info(f"{data=}\n")

    try:
        await add_data_to_redis(data)
    except:
        logging.exception('Error:')

    return "success", 200


# Функция для добавления данных в Redis канал
async def add_data_to_redis(data):
    r = await aioredis.from_url('redis://localhost', db=1, decode_responses=True)
    channel = 'payment_channel'
    json_data = json.dumps(data)
    await r.rpush(channel, json_data)

    await r.close()


@app.route("/test")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8093)
    logging.warning('Сервер отключен')
