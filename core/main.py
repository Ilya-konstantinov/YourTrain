import logging
import asyncio
import sys
import threading

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject
from aiogram.enums import ParseMode

from data.config import TOKEN
from FSMachines import MStates
from database.dataframe import DB
from handler.service import bl_set, bl_help, bl_start
from handler.req import bl_req, bl_mlt_req
from handler.cache_req import new_cache_req, get_cache_req
from handler.cache_path import cache_path, num_path, refr_sched

logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
dp = Dispatcher()
user_cache_path: dict[int, list]


@dp.message(Command("req"))
async def cmd_req(message: Message, command: CommandObject):
    ans = await bl_req(user_id=message.from_user.id, args=command.args)
    await message.answer(ans, parse_mode=ParseMode.MARKDOWN_V2)


@dp.message(Command("path_cache"))
async def cmd_path_cache(message: Message, command: CommandObject, state: FSMContext):
    await state.set_state(MStates.CachePath.get_path)
    ans = await cache_path(message.from_user.id, command.args)
    await message.answer(ans + "\nВыведите номер пути, который хотите добавить\n⠀", parse_mode=ParseMode.MARKDOWN_V2)


@dp.message(MStates.CachePath.get_path)
async def path_num(message: Message, state: FSMContext):
    await state.set_state(MStates.CachePath.num_path)
    ans = await num_path(message.from_user.id, message.text)
    await message.answer(ans)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    user_exists = DB.user_exist(user.id)

    if not user_exists:
        DB.user_create(user.id, user.first_name, message.chat.id)

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
    ans = await new_cache_req(user_id=message.from_user.id, args=command.args)
    await message.answer(ans)


@dp.message(Command("get"))
async def get_cache(message: Message, command: CommandObject):
    ans = await get_cache_req(message.from_user.id, command.args)
    await message.answer(ans, parse_mode=ParseMode.MARKDOWN_V2)


async def bot_start(bot) -> None:
    await dp.start_polling(bot)


async def main() -> None:
    bot = Bot(token=TOKEN)
    await asyncio.gather(bot_start(bot), refr_sched(bot))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
