from database.dataframe import DB
from handler.req import single_req_parse, multi_req_parse, mlt_ans, singe_ans
from data.answer_enums import CACHE_REQ
from model.arg_format import cor_name
from model.model import get_station


async def new_cache_req(user_id: int, args: str):
    """
    Создание нового сохранённого запроса.

    :param user_id: Уникальный id пользователя.
    :param args: Параметры в формате (name[, sort_type[, filter_type[, col]]])
    :return: Возвращает SUCCESS если путь создан успешно, 
        сообщение об ошибке в ином случае
    """
    filter_type, sort_type, col = DB.user_params(uid=user_id)[1:]
    is_mlt: bool = False

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

    for st in st_to:
        if not DB.station_exists(st):
            DB.station_create(st)

    for st in st_from:
        if not DB.station_exists(st):
            DB.station_create(st)

    DB.cache_req_create(user_id, name=name, is_mlt=is_mlt,
                        sort_type=sort_type, filter_type=filter_type,
                        col=col, dep_time=dep_time,
                        dep_st_id=[st.id for st in st_from], arr_st_id=[st.id for st in st_to])

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

    args = DB.cache_req_get(user_id, args)

    if not args:
        return CACHE_REQ.BAD_NAME

    stations, args, is_mlt = args

    if is_mlt:
        return mlt_ans(*stations, *args)
    else:
        return singe_ans(*stations, *args)

