import logging

from aiogram import Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from FSMachines import MStates
from keyboard import menu
from keyboard.req_inline import req_inline
from logic.cache_req import get_cache_req
from logic.service import bl_get_nearest_cache_req


def hand(dp: Dispatcher):
    @dp.message(Command("cancel"))
    @dp.message(F.text.casefold() == "отмена")
    async def cancel_handler(message: Message, state: FSMContext) -> None:
        """
        Allow user to cancel any action
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
        ans = await get_cache_req(message.from_user.id, message.text)
        if not ans[0] == '`':
            await message.answer(ans)
            return
        if await state.get_state():
            await state.clear()
        await state.set_state(MStates.Menu.just_menu)
        await message.answer(ans, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=req_inline(message.text))
        await message.answer("Меню", reply_markup=menu.menu(
                *bl_get_nearest_cache_req(message.from_user.id)
            ),)
