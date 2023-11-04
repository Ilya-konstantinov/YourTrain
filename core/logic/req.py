from data.answer_enums import BAD_REQUEST
from database.db_cache_req import DBCacheReq
from database.db_station import DBStation
from database.db_user import DBUser
from model.arg_format import time_arg, filter_arg, sort_arg, col_arg, cor_time
from model import model


async def bl_mlt_req(user_id: int, args: str, raw_ans: bool = False):
    if not args:
        return BAD_REQUEST.ZERO_ARGS

    if args.count(' ') == 0:
        return BAD_REQUEST.TOO_MANY_ARGS

    cor_args = multi_req_parse(user_id, args)
    if isinstance(cor_args, str):
        return cor_args

    return mlt_ans(*cor_args, raw_ans=raw_ans)


async def bl_req(user_id: int, args: str, raw_ans: bool = False):
    if not args:
        return BAD_REQUEST.ZERO_ARGS
    args = args.replace('..', ':')
    if args.count(' ') == 0:
        return BAD_REQUEST.TOO_MANY_ARGS

    args = single_req_parse(user_id, args)

    if isinstance(args, str):
        return args

    return singe_ans(*args, raw_ans=raw_ans)


def mlt_ans(st_from, st_to, dep_time, sort_type, filter_type, col, raw_ans):
    req: list[model.Path] = []
    dep_time = time_arg(dep_time)
    for fr in st_from:
        for to in st_to:
            req += model.req(station_from=fr, station_to=to, sort_type=sort_type, dep_time=dep_time,
                             filter_type=filter_type, col=col)
            req = model.paths_sort(req, sort_type)
            req = req[:col]

    if req is None:  # None if server fault
        return BAD_REQUEST.SERVER_ERROR

    if not req:  # Empty list if incorrect args or too late time
        return BAD_REQUEST.ZERO_ANSWER

    if raw_ans:
        return req
    else:
        return ans_format(req)


def singe_ans(st1, st2, dep_time, sort_type, filter_type, col, raw_ans):
    dep_time = time_arg(dep_time)
    req: list = model.req(station_from=st1, station_to=st2, dep_time=dep_time, sort_type=sort_type,
                          filter_type=filter_type, col=col)

    if req is None:  # None if server fault
        return BAD_REQUEST.SERVER_ERROR

    if not req:  # Empty list if incorrect args or too late time
        return BAD_REQUEST.ZERO_ANSWER

    if raw_ans:
        return req
    else:
        return ans_format(req)


def ans_format(req):
    ans = '\n'.join(
        [
            "```\n"+it.get_view()+"```" for it in req
        ]
    )
    if len(req) != 4:
        ans += '\n⠀'
    return ans


def single_req_parse(uid: int, args: str) -> str | tuple:
    args = args.split()
    st1, st2 = args[:2]
    try:
        int(st1)
        int(st2)
        assert len(st1) == len(st2) == 7
        st1, st2 = DBStation.station_by_id(int(st1)).title, DBStation.station_by_id(int(st2)).title
    except:
        ...
    cor_args = args_parse(uid, args[2:])

    if isinstance(cor_args, str):
        return cor_args

    dep_time, sort_type, filter_type, col = cor_args

    if not (model.get_station(st1) and model.get_station(st2)):
        return BAD_REQUEST.BAD_STATION

    return st1, st2, dep_time, sort_type, filter_type, col


def multi_req_parse(uid: int, args: str):
    st, args = args.split('\n')
    st_from, st_to = st.split(' -- ')
    st_from, st_to = st_from.split(), st_to.split()
    try:
        for st in st_from:
            int(st)
            assert len(st) == 7
        for st in st_to:
            int(st)
            assert len(st) == 7
        st_from = [DBStation.station_by_id(int(st)) for st in st_from]
        st_to = [DBStation.station_by_id(int(st)) for st in st_to]
    except:
        ...

    args = args.split()

    cor_args = args_parse(uid, args)

    if isinstance(cor_args, str):
        return cor_args

    dep_time, sort_type, filter_type, col = cor_args

    for st in st_from:
        if not model.get_station(st):
            return BAD_REQUEST.BAD_STATION

    for st in st_to:
        if not model.get_station(st):
            return BAD_REQUEST.BAD_STATION

    return st_from, st_to, dep_time, sort_type, filter_type, col


def args_parse(user_id, *args) -> str | tuple:
    sort_type, filter_type, col = DBUser.user_params(user_id)[1:]
    dep_time: str | None = None
    args = args[0]

    if len(args) > 0 and args[0] != '-':
        time: str = args[0]
        time: str = cor_time(time)
        if isinstance(time, str):
            return time
        dep_time = args[0]

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
        tmp_col = col_arg(args[3])
        if isinstance(col, str):
            return col
        col = tmp_col

    return dep_time, sort_type, filter_type, col


async def bl_all_req(uid: int) -> str:
    reqs = DBCacheReq.cache_req_whole_get(uid)
    if not reqs:
        return "Похоже, у вас нет сохранённых запросов"
    ans = f'`{"-"*30}`\n'.join([
        '```\n'+req.get_view()+'```' for req in reqs
    ])
    return ans


def check_station(st: str) -> str | None:
    if not model.get_station(st):
        return BAD_REQUEST.BAD_STATION

    return None