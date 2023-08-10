import asyncio
import logging

from aiogram.types import BotCommand

from create_bot import bot, dp
from environs import Env

from database import models
from handlers import user_handlers_private, admin_handlers, user_handlers, players_handlers, my_team_handlers

env = Env()
env.read_env()

# Инициализируем логгер
logger = logging.getLogger(__name__)


async def set_default_commands():
    await bot.set_my_commands(
        [
            BotCommand(command='/start', description='Перезапустить бота'),
        ]
    )

async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    '''Подключаем базу данных'''
    await models.db_connect()

    # Регистриуем роутеры в диспетчере
    dp.include_router(admin_handlers.router)
    dp.include_router(players_handlers.router)
    dp.include_router(my_team_handlers.router)
    dp.include_router(user_handlers_private.router)
    dp.include_router(user_handlers.router)
    # dp.include_router(user_handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

