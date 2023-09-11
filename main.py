import logging
import asyncio
import sys
import model

from aiogram import Bot, Dispatcher, types
from config import TOKEN
from aiogram import F
from aiogram.filters import Command, CommandObject

logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
dp = Dispatcher()

@dp.message(Command('start', 'help'))
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    s = "012345678901234567890123456789"
    await message.reply(s)
    
@dp.message(Command("req"))
async def cmd_name(message: types.Message, command: CommandObject):
    col: int = 5
    if command.args:
        if command.args.count(' ') == 1:
            st1, st2 = command.args.split()
            ans = '\n'.join(
                [
                    it.get_view() for it in model.req(st1, st2, 5)
                ]
            )
            await message.answer(f"{ans}")
        else:
            await message.answer('В команде должен быть только один пробел -- разделяющий станции')
    else:
        await message.answer("Пожалуйста, укажи своё имя после команды /name!")

async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)
    
 
if __name__ == '__main__':  
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())