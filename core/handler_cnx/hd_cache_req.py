from aiogram import Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from FSMachines import MStates
from keyboard import cache_req_inline
from logic.cache_req import new_cache_req, get_cache_req
from logic.req import bl_all_req
from database.db_cache_req import DBCacheReq


def hand(dp: Dispatcher):
    @dp.message(Command("cache"))
    async def cache(message: Message, command: CommandObject):
        ans = await new_cache_req(user_id=message.from_user.id, args=command.args)
        await message.answer(ans)

    @dp.message(Command("all_req"))
    @dp.message(MStates.Menu.just_menu, F.text.casefold() == "сохранённые запросы")
    async def cmd_all_req(message: Message):
        ans = await bl_all_req(message.from_user.id)

        await message.answer(ans,
                             parse_mode=ParseMode.MARKDOWN_V2,
                             reply_markup=cache_req_inline.cache_req_inline(
                                     DBCacheReq.cache_req_whole_get(message.from_user.id)
                                )
                             )

    @dp.message(MStates.CacheRequest.get_name)
    async def get_name(message: Message, state: FSMContext):
        name = message.text
        params = (await state.get_data())['params']
        params = name + ' ' + params
        ans = await new_cache_req(message.from_user.id, params)
        await message.answer(ans)

    @dp.message(Command("get"))
    async def get_cache(message: Message, command: CommandObject):
        ans = await get_cache_req(message.from_user.id, command.args)
        if ans[0] != '`':
            await message.answer(ans)
            return
        await message.answer(ans, parse_mode=ParseMode.MARKDOWN_V2)

    @dp.message(MStates.Menu.just_menu, F.text)
    async def get_cache(message: Message):
        ans = await get_cache_req(message.from_user.id, message.text)
        await message.answer(ans, parse_mode=ParseMode.MARKDOWN_V2)

