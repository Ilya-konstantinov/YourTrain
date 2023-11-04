import logging
import asyncio
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from data.config import TOKEN
from FSMachines import MStates
from logic.cache_path import refr_sched
from keyboard import menu
from handler_cnx import hd_cache_path, hd_cache_req, hd_req, hd_settings, hd_service
from logic.service import bl_get_nearest_cache_req

logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
dp = Dispatcher()


@dp.message(Command('menu'))
async def cmd_menu(message: Message, state: FSMContext):
    await state.set_state(MStates.Menu.just_menu)
    await message.answer(text="Вот твое меню ссаное", reply_markup=(menu.menu(
        bl_get_nearest_cache_req(message.from_user.id)
    )))


@dp.message(Command("cancel"))
@dp.message(F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=menu.menu(
            bl_get_nearest_cache_req(message.from_user.id)
        ),
    )


async def bot_start(bot) -> None:
    await dp.start_polling(bot)


async def main() -> None:
    bot = Bot(token=TOKEN)

    hd_cache_path.hand(dp)
    hd_req.hand(dp)
    hd_service.hand(dp)
    hd_settings.hand(dp)
    hd_cache_req.hand(dp)

    await asyncio.gather(bot_start(bot), refr_sched(bot))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
