import datetime

from aiogram.types import Message
from aiogram.filters import CommandObject
from aiogram.enums import ParseMode
from core.model import model
from core.model.arg_format import *


async def bl_mlt_req(message: Message, command: CommandObject, col: int = 5):
    if not command.args:
        await message.answer(BAD_REQEST.ZERO_ARGS)
        return

    if command.args.count(' ') == 0:
        await message.answer(BAD_REQEST.TOO_MANY_ARGS)
        return

    st, args = command.args.split('\n')
    st_from, st_to = st.split(' -- ')
    st_from, st_to = st_from.split(), st_to.split()

    filter_type: int = 0
    sort_type: int = 0
    col: int = 5
    dep_time: datetime = datetime.datetime.now()

    if len(args) > 0:
        time = args[0]
        tmp_time = time_arg(time=time, dep_time=dep_time)
        if isinstance(tmp_time, str):
            await message.answer(tmp_time)
            return

        dep_time = tmp_time

    if len(args) > 1:
        tmp_sort = sort_arg(args[1])
        if isinstance(tmp_sort, str):
            await message.answer(tmp_sort)
            return
        else:
            sort_type = tmp_sort

    if len(args) > 2:
        tmp_filter = filter_arg(args[2])
        if isinstance(tmp_filter, str):
            await message.answer(tmp_filter)
            return
        else:
            filter_type = tmp_filter

    if len(args) > 5:
        try:
            col = int(args[5])
            if not (1 <= col <= 20):
                raise "Bad args"
        except:
            await message.answer(BAD_REQEST.BAD_COL)
            return

    ans: list = []

    for fr in st_from:
        for to in st_to:
            ans += model.req(station_from=fr, station_to=to, sort_type=sort_type, dep_time=dep_time,
                             filter_type=filter_type)
            model.paths_sort(ans, sort_type)
            ans = ans[:col]


async def bl_req(message: Message, command: CommandObject, col: int = 5):
    if not command.args:
        await message.answer(BAD_REQEST.ZERO_ARGS)
        return

    if command.args.count(' ') == 0:
        await message.answer(BAD_REQEST.TOO_MANY_ARGS)
        return

    sort_type: int = 0  # Default for sort (departure time)
    filter_type: int = 0  # Default for filter (all)
    dep_time = datetime.now()
    args = command.args.split()
    st1 = args[0]
    st2 = args[1]
    if len(args) > 2:
        time = args[2]
        tmp_time = time_arg(time=time, dep_time=dep_time)
        if isinstance(tmp_time, str):
            await message.answer(tmp_time)
            return

        dep_time = tmp_time

    if len(args) > 3:
        tmp_sort = sort_arg(args[3])
        if isinstance(tmp_sort, str):
            await message.answer(tmp_sort)
            return
        else:
            sort_type = tmp_sort

    if len(args) > 4:
        tmp_filter = filter_arg(args[4])
        if isinstance(tmp_filter, str):
            await message.answer(tmp_filter)
            return
        else:
            filter_type = tmp_filter

    if len(args) > 5:
        try:
            col = int(args[5])
            if not (1 <= col <= 20):
                raise "Bad args"
        except:
            await message.answer(BAD_REQEST.BAD_COL)
            return

    req: list = model.req(station_from=st1, station_to=st2, dep_time=dep_time, sort_type=sort_type,
                          filter_type=filter_type, col=col)

    if req is None:  # None if server fault
        await message.answer(BAD_REQEST.SERVER_ERROR)
        return

    if not req:  # Empty list if incorrect args or too late time
        await message.answer(BAD_REQEST.ZERO_ANSWER)
        return

    ans = f'\n{"-" * 30}\n'.join(
        [
            it.get_view() for it in req
        ]
    )
    ans = '```\n' + ans + '```'
    if len(req) != 4:
        ans += '\n⠀'
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
