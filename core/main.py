import logging
import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from data.config import TOKEN
from aiogram import F
from aiogram.filters import Command, CommandObject
from handler.basic import bl_req, bl_help

logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
dp = Dispatcher()
    
@dp.message(Command("req"))
async def cmd_req(message: Message, command: CommandObject):
    col: int = 5
    await bl_req(message, command, col)
        

@dp.message(Command("help", "start"))        
async def cmd_help(message: Message, command: CommandObject):
    await bl_help(message, command)


async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)
    
 
if __name__ == '__main__':  
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())