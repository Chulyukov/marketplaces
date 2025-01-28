import logging
import os
import qrcode
import asyncio
from io import BytesIO
import base64
from datetime import datetime
from logging.handlers import RotatingFileHandler

import redis
from quart import Quart, render_template

from config import Config
from db.db_queries import db_get_emoji_from_two_tables, db_get_ru_name_from_two_tables
from link_for_marketplace.db_link import db_get_date, db_switch_status_on_activated, \
    db_update_iccid_and_activation_code, db_get_link_status, db_fill_date
from monty_api import MontyApi

# Инициализация Quart и Redis
app = Quart(__name__, static_folder='static')
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

CACHE_TTL = 120  # TTL для кэширования в секундах

# Формируем путь относительно текущего файла
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs/error_page.log")

# Настройка логирования
log_formatter = logging.Formatter(
    "\n%(asctime)s - %(levelname)s - %(message)s => %(exc_info)s"
)

# Создаём обработчик для записи в файл
file_handler = RotatingFileHandler(log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5)
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(log_formatter)

# Настройка основного логгера
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Логируем только ERROR и выше
logger.addHandler(file_handler)


async def generate_qr_code(activation_code: str) -> str:
    """
    Асинхронно генерирует QR-код для строки активации eSIM.
    :param activation_code: Строка активации eSIM (LPA:...)
    :return: Base64-кодированный QR-код
    """

    def create_qr():
        # Генерация QR-кода
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(activation_code)
        qr.make(fit=True)

        # Сохранение QR-кода в буфер
        buffer = BytesIO()
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    # Выполнение генерации QR-кода в отдельном потоке
    buffer = await asyncio.to_thread(create_qr)

    # Преобразование изображения в base64
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return qr_code_base64


def get_country_info(country):
    """Получение информации о стране (название и эмодзи)"""
    emoji = db_get_emoji_from_two_tables(country)
    country_name = db_get_ru_name_from_two_tables(country).capitalize()
    return f"{country_name} {emoji}"


def cache_page(key, ttl, page_content):
    """Кэширование страницы"""
    redis_client.setex(key, ttl, page_content)


async def render_esim_page(country, gb_amount, ios_link, qr_code, instructions_link):
    """Рендеринг страницы eSIM"""
    return await render_template(
        'welcome.html',
        country=country,
        gb_amount=gb_amount,
        ios_universal_installation_link=ios_link,
        qr_code=qr_code,
        instructions_link=instructions_link,
    )


async def render_expired_page():
    """Рендеринг страницы истечения срока действия eSIM"""
    return await render_template(
        'expired_date_page.html',
        direct_bot_link=Config.BOT_LINK,
    )


async def render_error_page(bundle_code: str):
    """Рендеринг страницы с ошибкой"""
    return await render_template(
        'error_page.html',
        bundle_code=bundle_code
    )


@app.route('/<country>/<gb_amount>/<uuid>')
async def welcome_page(country: str, gb_amount: str, uuid: str):
    cache_key = f"esim:{country}:{gb_amount}:{uuid}"

    # Проверка кэша
    cached_page = redis_client.get(cache_key)
    if cached_page:
        return cached_page

    bundle_code = ""

    try:
        status = db_get_link_status(uuid)
        if status == "unactivated":
            db_fill_date(uuid)

        date = db_get_date(uuid)
        if (datetime.now() - date).days >= 30:
            return await render_expired_page()

        monty = MontyApi()
        if status == "unactivated":
            bundle_code = monty.get_necessary_bundle_code(country, gb_amount)
            monty.activate_esim(bundle_code, uuid)
            esim_info = monty.get_esim_info(uuid)

            db_switch_status_on_activated(uuid)
            db_update_iccid_and_activation_code(esim_info["iccid"], esim_info["activation_code"], uuid)
        else:
            esim_info = monty.get_esim_info(uuid)
            gb_amount = monty.get_remaining_data(esim_info["order_id"])

        ios_link = f"https://esimsetup.apple.com/esim_qrcode_provisioning?carddata={esim_info["activation_code"]}"
        qr_code = await generate_qr_code(esim_info["activation_code"])
        country_info = get_country_info(country)

        rendered_page = await render_esim_page(country_info, f"{gb_amount}.0", ios_link, qr_code, Config.QUESTIONS_LINK)
        cache_page(cache_key, CACHE_TTL, rendered_page)
        return rendered_page

    except Exception as e:
        # Логируем только ошибки
        logger.error(f"{uuid} : {str(e)}\n", exc_info=True)
        return await render_error_page(bundle_code), 500


if __name__ == '__main__':
    app.run(ssl_context=('../cert.pem', '../key.pem'), host='0.0.0.0', port=443)
