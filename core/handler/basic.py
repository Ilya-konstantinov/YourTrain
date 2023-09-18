import datetime
import re

from datetime import timedelta
from data.answer_enums import BAD_REQEST, HELP
from aiogram.types import Message
from aiogram.filters import CommandObject
from aiogram.enums import ParseMode
from datetime import datetime
from model import model


sort_dict = {
    ('dpt', 'departure_time', '0') : 0,
    ('1','arrival_time','art') : 1,
    ('2', 'path_time','pht') : 2
}


filter_dict = {
    ("all", '0') : 0,
    ("1", 'speed', 'sd') : 1,
    ('2', 'rg') : 2,
}



async def bl_req(message: Message, command: CommandObject, col: int):
    if not command.args:
        await message.answer(BAD_REQEST.ZERO_ARGS)
        return
    
    if command.args.count(' ') == 0:
        await message.answer(BAD_REQEST.TOO_MANY_ARGS)
        return
    
    sort_type:int = 0 ## Default for sort (departure time)
    filter_type:int = 0 ## Default for filter (all)
    dep_time = datetime.now()
    args = command.args.split()
    st1 = args[0]
    st2 = args[1]
    
    if (len(args) > 2):
        if (re.fullmatch(r'(\+|-)\d+', args[2])):
            dep_time += (1 if args[2][0] == '+' else -1) * timedelta(minutes=int(args[2][1:]))
        elif args[2] == '0':
            ...
        elif (re.fullmatch(r'[0-2]?[0-9]\.[0-5][0-9]', args[2])):
            tmp_time = datetime.strptime(args[2], "%H.%M")
            dep_time = dep_time.replace(hour=tmp_time.hour, minute=tmp_time.minute)
        elif (re.fullmatch(r'[0-2]?[0-9]:[0-5][0-9]', args[2])):
            tmp_time = datetime.strptime(args[2], "%H:%M")
            dep_time = dep_time.replace(hour=tmp_time.hour, minute=tmp_time.minute)
        else:
            await message.answer(BAD_REQEST.BAD_TIME)
            return
    
    if (len(args) > 3):
        for tp in sort_dict:
            if (args[3] in tp):
                sort_type = sort_dict[tp]
                break
        else:
            await message.answer(BAD_REQEST.BAD_SORT)
            return
    
    if (len(args) > 4):
        for tp in filter_dict:
            if (args[4] in tp):
                filter_type = filter_dict[tp]
                break
        else:
            await message.answer(BAD_REQEST.BAD_FILTER)
            return
            
    if (len(args) > 5):
        try:
            col = int(args[5])
            if not (1 <= col <= 20):
                raise "Bad args" 
        except:
            await message.answer(BAD_REQEST.BAD_COL)
            return
    

    req:list = model.req( station_from= st1, station_to= st2, dep_time=dep_time , sort_type= sort_type, filter_type= filter_type, col= col) 
    
    if (req is None): ## None if server fault
        await message.answer(BAD_REQEST.SERVER_ERROR)
        return
    
    if (req == []): ## Empty list if incorrect agrs or too late time
        await message.answer(BAD_REQEST.ZERO_ANSWER)
        return
    
    ans = f'\n{"-"*30}\n'.join(
        [
            it.get_view() for it in req
        ]
    )
    
    ans = '```\n'+ans+'```'
    await message.answer(f"{ans}", parse_mode=ParseMode.MARKDOWN_V2)
    
async def bl_help(message: Message, command: CommandObject):
    match command.args:
        case None:
            await message.answer(HELP.BASE)
        case "req":
            await message.answer(HELP.REQ)
        case _:
            await message.answer(HELP.BASE)
    return