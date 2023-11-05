from aiogram import Dispatcher
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from data.answer_enums import EDUC
from database.db_user import DBUser
from keyboard import menu
from logic.service import bl_start, bl_help, bl_recache_user, bl_get_nearest_cache_req


def hand(dp: Dispatcher):
    """
    Внесение функций в хендлер
    """
    @dp.message(Command("start"))
    async def cmd_start(message: Message):
        """
        Начинает работу с пользователем и заносит его в БД.
        """
        user = message.from_user
        user_exists = DBUser.user_exist(user.id)

        if not user_exists:
            DBUser.user_create(user.id, user.first_name, message.chat.id)

        ans = await bl_start(user_id=user.id, user_exists=user_exists)
        await message.answer(ans)
        await message.answer(EDUC.CLASSIC, reply_markup=menu.menu(
            *bl_get_nearest_cache_req(message.from_user.id)
        ))

    @dp.message(Command("educ"))
    async def cmd_educ(message: Message, command: CommandObject):
        """
        Вызывает обучение пользователя (продвинутое или нет)
        """
        if command.args is None:
            await message.answer(EDUC.CLASSIC, reply_markup=menu.menu(
                *bl_get_nearest_cache_req(message.from_user.id)
            ))
        else:
            await message.answer(EDUC.WHOLE, reply_markup=menu.menu(
                *bl_get_nearest_cache_req(message.from_user.id)
            ))

    @dp.message(Command("help"))
    async def cmd_help(message: Message, command: CommandObject):
        """
        Вызывает документацию для какой-либо команды бота.
        """
        ans = await bl_help(user_id=message.from_user.id, args=command.args)
        await message.answer(ans)

    @dp.message(Command("recache_user"))
    async def cmd_recache_user(message: Message):
        """
        Меняет все настройки пользователя на настройки по умолчанию
        """
        ans = await bl_recache_user(message.from_user.id, message.from_user.first_name)
        await message.answer(ans)
