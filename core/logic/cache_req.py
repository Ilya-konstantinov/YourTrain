from database.db_cache_req import DBCacheReq
from logic.req import single_req_parse, multi_req_parse, mlt_ans, singe_ans
from data.answer_enums import CACHE_REQ
from model.arg_format import cor_name, time_arg
from model.model import get_station
from model.path import CacheRequest


async def new_cache_req(user_id: int, args: str):
    """
    Создание нового сохранённого запроса.

    :param user_id: Уникальный id пользователя.
    :param args: Параметры в формате (name, st_from, st_to[, sort_type[, filter_type[, col]]])
    :return: Возвращает SUCCESS если путь создан успешно, 
        сообщение об ошибке в ином случае
    """

    is_mlt = args.find('--') != -1
    name = args.split()[0]

    if not cor_name(args[0]):
        return CACHE_REQ.BAD_NAME
    parse_f = multi_req_parse if is_mlt else single_req_parse
    cor_args = parse_f(user_id, args[args.find(' ') + 1:])
    if isinstance(cor_args, str):
        return cor_args
    st_from, st_to, dep_time, sort_type, filter_type, col = cor_args

    if not is_mlt:
        st_from, st_to = [get_station(st_from)], [get_station(st_to)]
    else:
        st_to = [get_station(i) for i in st_to]
        st_from = [get_station(i) for i in st_from]

    if not DBCacheReq.cache_req_create(
        CacheRequest(
            dep_st=st_from, arr_st=st_to,
            dep_time=dep_time, filter_type=filter_type, sort_type=sort_type, col=col,
            is_mlt=is_mlt, user_id=user_id, name=name
        )
    ):
        return CACHE_REQ.UNSUCCESS

    return CACHE_REQ.SUCCESS


async def get_cache_req(user_id: int, args: str) -> str:
    """
    Возвращает ответ на сохранённый запрос.

    :param user_id: Уникальный id пользователя.
    :param args: Идентификация пути для пользователя (name/number).
    :return: Возвращает пути или значение ошибки.
    """
    if not cor_name(args):
        return CACHE_REQ.BAD_NAME

    args = DBCacheReq.cache_req_get(user_id, args)

    if not args:
        return CACHE_REQ.BAD_NAME
    stations, args, is_mlt = (args.dep_st, args.arr_st), (args.dep_time, args.sort_type, args.filter_type, args.col), args.is_mlt
# st_from, st_to, dep_time, sort_type, filter_type, col, raw_ans
    if is_mlt:
        return mlt_ans(*stations, *args, raw_ans=False)
    else:
        return singe_ans(*(stations[0][0], stations[1][0]), *args, raw_ans=False)

