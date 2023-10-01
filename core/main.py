import logging
import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from data.config import TOKEN
from aiogram.filters import Command, CommandObject
from handler.service import bl_set, bl_help, bl_start
from handler.req import bl_req, bl_mlt_req
from handler.cache import new_cache_path
from aiogram.enums import ParseMode
from database.dataframe import DB

logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
dp = Dispatcher()


@dp.message(Command("req"))
async def cmd_req(message: Message, command: CommandObject):
    ans = await bl_req(user_id=message.from_user.id, args=command.args)
    await message.answer(ans, parse_mode=ParseMode.MARKDOWN_V2)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    user_exists = DB.user_exist(user.id)

    if not user_exists:
        DB.user_create(user.id, user.first_name)

    ans = await bl_start(user_id=user.id, user_exists=user_exists)
    await message.answer(ans)


@dp.message(Command("help"))
async def cmd_help(message: Message, command: CommandObject):
    ans = await bl_help(user_id=message.from_user.id, args=command.args)
    await message.answer(ans)


@dp.message(Command("multi_req", "mltreq"))
async def mlt_req(message: Message, command: CommandObject):
    ans = await bl_mlt_req(user_id=message.from_user.id, args=command.args)
    await message.answer(ans, parse_mode=ParseMode.MARKDOWN_V2)


@dp.message(Command("set"))
async def set_par(message: Message, command: CommandObject):
    ans = await bl_set(user_id=message.from_user.id, args=command.args)
    await message.answer(ans)


@dp.message(Command("cache"))
async def cache(message: Message, command: CommandObject):
    ans = await new_cache_path(user_id=message.from_user.id, args=command.args)
    await message.answer(ans)


async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
