from dataclasses import dataclass

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties


@dataclass
class Config:
    # Полная ссылка на бота
    BOT_LINK = "https://t.me/esim_unity_bot"

    # BNESIM креды
    BNESIM_PARTNER_LOGIN = "nikita.admin"
    BNESIM_API_KEY = "pe2mp9qxcen9"

    # БД
    DB_HOST = "213.108.20.201"
    DB_NAME = "esim_db"
    DB_USER = "esim_user"
    DB_PASS = "Kexibq528123!"

    # Ссылка на популярные вопросы в Telegraph
    QUESTIONS_LINK = "https://telegra.ph/CHto-takoe-eSIM-07-27"

    # YAM API
    YAM_API_KEY = "ACMA:X5fc6XGwua2rD7YTWzD4leXSeCc7tYrxlN3T9KqR:c8b5d4b4"
    YAM_CAMPAIGN_ID = 130152372

    # Monty API
    MONTY_LOGIN = "esimunity"
    MONTY_PASSWORD = "Qa4!Qt8)Nt9)"
