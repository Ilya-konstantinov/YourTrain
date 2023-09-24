import datetime

from core.model import model
from core.model.arg_format import *
from core.database.dataframe import DB


async def bl_mlt_req(user_id: int, args: str):
    if not args:
        return BAD_REQEST.ZERO_ARGS

    if args.count(' ') == 0:
        return BAD_REQEST.TOO_MANY_ARGS

    st, args = args.split('\n')
    st_from, st_to = st.split(' -- ')
    st_from, st_to = st_from.split(), st_to.split()
    args = args.split()

    filter_type, sort_type, col = DB.user_params(user_id=user_id)[1:]
    dep_time: datetime = datetime.now()

    if len(args) > 0:
        time = args[0]
        tmp_time = time_arg(time=time, dep_time=dep_time)
        if isinstance(tmp_time, str):
            return tmp_time
        dep_time = tmp_time

    if len(args) > 1:
        tmp_sort = sort_arg(args[1])
        if isinstance(tmp_sort, str):
            return tmp_sort
        else:
            sort_type = tmp_sort

    if len(args) > 2:
        tmp_filter = filter_arg(args[2])
        if isinstance(tmp_filter, str):
            return tmp_filter
        else:
            filter_type = tmp_filter

    if len(args) > 5:
        try:
            col = int(args[5])
            if not (1 <= col <= 20):
                raise "Bad args"
        except:
            return BAD_REQEST.BAD_COL

    req: list[model.Path] = []

    for fr in st_from:
        for to in st_to:
            req += model.req(station_from=fr, station_to=to, sort_type=sort_type, dep_time=dep_time,
                             filter_type=filter_type, col=col)
            req = model.paths_sort(req, sort_type)
            req = req[:col]

    if req is None:  # None if server fault
        return BAD_REQEST.SERVER_ERROR

    if not req:  # Empty list if incorrect args or too late time
        return BAD_REQEST.ZERO_ANSWER

    ans: str = f'\n{"-" * 30}\n'.join(
        [
            it.get_view() for it in req
        ]
    )
    if ans.find("Через") == -1:
        ans += '\n⠀'
    ans = '```\n' + ans + '```'

    return ans


async def bl_req(user_id: int, args: str):
    if not args:
        return BAD_REQEST.ZERO_ARGS

    if args.count(' ') == 0:
        return BAD_REQEST.TOO_MANY_ARGS

    filter_type, sort_type, col = DB.user_params(user_id)[1:]
    dep_time: datetime = datetime.now()
    args = args.split()
    st1 = args[0]
    st2 = args[1]
    if len(args) > 2:
        time = args[2]
        tmp_time = time_arg(time=time, dep_time=dep_time)
        if isinstance(tmp_time, str):
            return tmp_time

        dep_time = tmp_time

    if len(args) > 3:
        tmp_sort = sort_arg(args[3])
        if isinstance(tmp_sort, str):
            return tmp_sort
        else:
            sort_type = tmp_sort

    if len(args) > 4:
        tmp_filter = filter_arg(args[4])
        if isinstance(tmp_filter, str):
            return tmp_filter
        else:
            filter_type = tmp_filter

    if len(args) > 5:
        try:
            col = int(args[5])
            if not (1 <= col <= 20):
                raise "Bad args"
        except:
            return BAD_REQEST.BAD_COL

    req: list = model.req(station_from=st1, station_to=st2, dep_time=dep_time, sort_type=sort_type,
                          filter_type=filter_type, col=col)

    if req is None:  # None if server fault
        return BAD_REQEST.SERVER_ERROR

    if not req:  # Empty list if incorrect args or too late time
        return BAD_REQEST.ZERO_ANSWER

    ans = f'\n{"-" * 30}\n'.join(
        [
            it.get_view() for it in req
        ]
    )
    ans = '```\n' + ans + '```'
    if len(req) != 4:
        ans += '\n⠀'
    return ans


async def bl_start(user_id: int, user_exists: bool):
    user_name = DB.user_params(user_id)[0]
    if user_exists:
        return HELP.START_OLD.format(user_name)
    else:
        return HELP.START_NEW.format(user_name)


async def bl_help(user_id: int, args: str):
    user_name = DB.user_params(user_id)[0]
    match args:
        case None:
            return HELP.BASE.format(user_name)
        case "req":
            return HELP.REQ
        case _:
            return HELP.BASE.format(user_name)


async def bl_set(user_id: int, args: str):
    if not args:
        return HELP.SET

    args = args.split()

    if len(args) != 2:
        return SET.BAD_COL

    column_name = param_arg(args[0])
    if column_name not in type_interp.values():
        return column_name

    val: str = param_var(args[1])

    if column_name == "name":
        if not cor_name(val):
            return SET.BAD_VAR
    elif column_name == "col":
        try:
            val = int(val)
            if not (1 <= int(val) <= 20):
                return SET.BAD_VAR
        except:
            return SET.BAD_VAR
    else:
        if val not in sort_dict.values():
            return SET.BAD_VAR
    DB.set_params(uid=user_id, param_val=val, param_key=column_name)

    return SET.SUCCESS.format(args[0], args[1])
