import logging

from aiogram import Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from FSMachines import MStates
from keyboard import menu
from logic.cache_req import get_cache_req
from logic.req import bl_req
from logic.service import bl_get_nearest_cache_req


def hand(dp: Dispatcher):
    """
    Внесение функций в хендлер
    """

    @dp.message(Command("cancel"))
    @dp.message(F.text.casefold() == "отмена")
    async def cancel_handler(message: Message, state: FSMContext) -> None:
        """
        Отмена любого действия и переход к базовому меню.
        """
        current_state = await state.get_state()
        if current_state:
            logging.info("Cancelling state %r", current_state)
            await state.clear()

        await state.set_state(MStates.Menu.just_menu)
        await message.answer(
            "Возвращаю",
            reply_markup=menu.menu(
                *bl_get_nearest_cache_req(message.from_user.id)
            ),
        )

    @dp.message(F.text)
    async def get_cache(message: Message, state: FSMContext):
        """
        Восприятие любого запроса как запрос сохранённого запроса.
        Если запрос не подходит как сохранённый, он воспринимает его как обычный запрос
        """
        f = bl_req if message.text.count(' ') else get_cache_req
        await state.set_state(MStates.Menu.just_menu)
        ans = await f(message.from_user.id, message.text)
        if not ans[0] == '`':
            await message.answer(ans, reply_markup=menu.menu(
                *bl_get_nearest_cache_req(message.from_user.id)
            ))
            return

        await message.answer(ans, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=menu.menu(
            *bl_get_nearest_cache_req(message.from_user.id)
        ))
