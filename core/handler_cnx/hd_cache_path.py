from aiogram import Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from FSMachines import MStates
from logic.cache_path import cache_path, num_path


def hand(dp: Dispatcher):
    @dp.message(Command("path_cache"))
    async def cmd_path_cache(message: Message, command: CommandObject, state: FSMContext):
        await state.set_state(MStates.CachePath.get_path)
        ans = await cache_path(message.from_user.id, command.args)
        await message.answer(ans + "\nВыведите номер пути, который хотите добавить\n⠀",
                             parse_mode=ParseMode.MARKDOWN_V2)

    @dp.message(MStates.CachePath.get_path)
    async def path_num(message: Message, state: FSMContext):
        await state.set_state(MStates.CachePath.num_path)
        ans = await num_path(message.from_user.id, message.text)
        await message.answer(ans)
