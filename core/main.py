import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from FSMachines import MStates
from data.config import TOKEN
from handler_cnx import hd_cache_path, hd_cache_req, hd_req, hd_settings, hd_service, hd_end
from keyboard import menu
from logic.cache_path import refr_sched
from logic.service import bl_get_nearest_cache_req

logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
dp = Dispatcher()


@dp.message(Command('menu'))
async def cmd_menu(message: Message, state: FSMContext):
    """
    Вызов основного меню
    """
    await state.set_state(MStates.Menu.just_menu)
    await message.answer(text="Вот твое меню", reply_markup=(menu.menu(
        *bl_get_nearest_cache_req(message.from_user.id)
    )))


async def main() -> None:
    """
    Главная функция для связи обработчика запросов с самими запросами
    """
    bot = Bot(token=TOKEN)

    hd_cache_path.hand(dp)
    hd_req.hand(dp)
    hd_service.hand(dp)
    hd_settings.hand(dp)
    hd_cache_req.hand(dp)
    hd_end.hand(dp)

    await asyncio.gather(bot_start(bot), refr_sched(bot))


async def bot_start(bot: Bot) -> None:
    """
    Асинхронная работа `bot`
    :param bot: `bot` для асинхронной работы
    """
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
