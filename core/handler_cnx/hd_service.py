from aiogram import Dispatcher
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from data.answer_enums import EDUC
from logic.service import bl_start, bl_help, bl_recache_user
from database.db_user import DBUser


def hand(dp: Dispatcher):
    @dp.message(Command("start"))
    async def cmd_start(message: Message):

        user = message.from_user
        user_exists = DBUser.user_exist(user.id)

        if not user_exists:
            DBUser.user_create(user.id, user.first_name, message.chat.id)

        ans = await bl_start(user_id=user.id, user_exists=user_exists)
        await message.answer(ans)
        await message.answer(EDUC.CLASSIC)

    @dp.message(Command("educ"))
    async def cmd_educ(message: Message, command: CommandObject):
        if command.args is None:
            await message.answer(EDUC.CLASSIC)
        else:
            await message.answer(EDUC.WHOLE)

    @dp.message(Command("help"))
    async def cmd_help(message: Message, command: CommandObject):
        ans = await bl_help(user_id=message.from_user.id, args=command.args)
        await message.answer(ans)

    @dp.message(Command("recache_user"))
    async def cmd_recache_user(message: Message, command: CommandObject):
        ans = await bl_recache_user(message.from_user.id, message.from_user.first_name)
        await message.answer(ans)
