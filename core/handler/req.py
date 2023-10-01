from datetime import datetime
from core.data.answer_enums import BAD_REQEST
from core.database.dataframe import DB
from core.model.arg_format import time_arg, filter_arg, sort_arg
from core.model import model


async def bl_mlt_req(user_id: int, args: str):
    if not args:
        return BAD_REQEST.ZERO_ARGS

    if args.count(' ') == 0:
        return BAD_REQEST.TOO_MANY_ARGS

    cor_args = multi_req_parse(user_id, args)
    if isinstance(cor_args, str):
        return cor_args

    return mlt_ans(*cor_args)


async def bl_req(user_id: int, args: str):
    if not args:
        return BAD_REQEST.ZERO_ARGS

    if args.count(' ') == 0:
        return BAD_REQEST.TOO_MANY_ARGS

    args = single_req_parse(user_id, args)

    if isinstance(args, str):
        return args

    return singe_ans(*args)


def mlt_ans(st_from, st_to, dep_time, sort_type, filter_type, col):
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


def singe_ans(st1, st2, dep_time, sort_type, filter_type, col):
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

def single_req_parse(uid: int, args: str) -> str | tuple:
    args = args.split()
    st1, st2 = args[:2]

    cor_args = args_parse(uid, args[2:])

    if isinstance(cor_args, str):
        return cor_args

    dep_time, sort_type, filter_type, col = cor_args

    if not (model.get_station(st1) and model.get_station(st2)):
        return BAD_REQEST.BAD_STATION

    return st1, st2, dep_time, sort_type, filter_type, col


def multi_req_parse(uid: int, args: str):
    st, args = args.split('\n')
    st_from, st_to = st.split(' -- ')

    st_from, st_to = st_from.split(), st_to.split()
    args = args.split()

    cor_args = args_parse(uid, args)

    if isinstance(cor_args, str):
        return cor_args

    dep_time, sort_type, filter_type, col = cor_args

    for st in st_from:
        if not model.get_station(st):
            return BAD_REQEST.BAD_STATION

    for st in st_to:
        if not model.get_station(st):
            return BAD_REQEST.BAD_STATION

    return st_from, st_to, dep_time, sort_type, filter_type, col


def args_parse(user_id, *args) -> str | tuple:
    sort_type, filter_type, col = DB.user_params(user_id)[1:]
    dep_time: datetime = datetime.now()
    args = args[0]

    if len(args) > 0 and args[0] != '-':
        time = args[0]
        tmp_time = time_arg(time=time)
        if isinstance(tmp_time, str):
            return tmp_time

        dep_time = tmp_time

    if len(args) > 1 and args[1] != '-':
        tmp_sort = sort_arg(args[1])
        if isinstance(tmp_sort, str):
            return tmp_sort

        sort_type = tmp_sort

    if len(args) > 2 and args[2] != '-':
        tmp_filter = filter_arg(args[2])
        if isinstance(tmp_filter, str):
            return tmp_filter
        filter_type = tmp_filter

    if len(args) > 3 and args[3] != '-':
        try:
            col = int(args[3])
            if not (1 <= col <= 20):
                raise "Bad args"
        except:
            return BAD_REQEST.BAD_COL

    return dep_time, sort_type, filter_type, col
