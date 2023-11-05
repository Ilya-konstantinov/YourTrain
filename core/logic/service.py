from data.answer_enums import HELP, SET, COMMENT, DEL_INFO, RECACHE
from database.db_cache_req import DBCacheReq
from database.db_del import DBDel
from database.db_recache import DBRecache
from database.db_user import DBUser
from model.arg_format import param_arg, param_var, is_cor_arg


async def bl_start(user_id: int, user_exists: bool) -> str:
    """
    Команда первого появления пользователя. Создает нового user с параметрами по умолчанию.
    :param user_id: Уникальный id пользователя.
    :param user_exists: Был ли пользователь зарегистрирован в системе ранее.
    :return: Возвращает приветсвие пользователю.
    """
    user_name = DBUser.user_params(user_id)[0]
    if user_exists:
        return HELP.START_OLD_F.format(user_name)
    else:
        return HELP.START_NEW_F.format(user_name)


async def bl_help(user_id: int, args: str) -> str:
    """
    Возвращает объяснение какой-либо команды пользователю.
    :param user_id: Уникальный id пользователя.
    :param args: На какой запрос нужен help.
    :return: Объяснение запроса или сообщение о неправильном запросе.
    """
    user_name = DBUser.user_params(user_id)[0]
    match args:
        case None:
            return HELP.BASE_F.format(user_name)
        case "req":
            return HELP.REQ
        case _:
            return HELP.BASE_F.format(user_name)


async def bl_set(user_id: int, args: str) -> str:
    """
    Изменяет какой-то параметр у пользователя с user_id.
    :param user_id: Уникальный id пользователя.
    :param args: Имя значения, которое надо изменить и новое значение.
    :return: Возвращает сообщение об успехе или ошибке.
    """
    if not args:
        return HELP.SET

    args = args.split()

    if len(args) != 2:
        return SET.BAD_COL
    val: str | int = param_var(args[1])
    column_name = param_arg(args[0])

    is_cor = is_cor_arg(column_name, val)

    if isinstance(is_cor, str):
        return is_cor

    DBUser.set_params(uid=user_id, param_val=val, param_key=column_name)

    return SET.SUCCESS_F.format(args[0], args[1])


async def bl_del_user_info(uid: int, name: str) -> str:
    """
    Удаляет информацию о пользователе.

    :param name: Имя пользователя.
    :param uid: Уникальный id пользователя.
    :return: Возвращает сообщение SUCCESS в случае успеха, UNSUCCESSFUL иначе.
    """

    is_suc = DBDel.del_info(uid, name)
    return DEL_INFO.SUCCESS if is_suc else DEL_INFO.UNSUCCESSFUL


def bl_comment_get_args(args: str) -> str | tuple[bool, str]:
    """
    Обрабатывает аргументы запроса на отзыв.

    :param args: Анонимен запрос или нет, на русском или bool.
    :return: Сообщение об ошибки если что-то пошло не так, или tuple[is_anon, ans] иначе.
    """
    args = args.strip()
    if args not in ['0', '1', "анонимно", "не анонимно"]:
        return COMMENT.UNSUCCESSFUL

    return args in ['1', 'анонимно'], COMMENT.GET_ARGS


async def bl_recache_user(uid: int, name: str) -> str:
    """
    Сбрасывает настройки пользователя на настройки по умолчанию.
    :param uid: Уникальный id пользователя.
    :param name: Стандартное имя пользователя, которое будет установлено в качестве имени по умолчанию.
    :return: Возвращаешь строку ошибки или успеха.
    """
    try:
        DBRecache.recache_user(uid, name)
    except:
        return RECACHE.USER_ERROR

    return RECACHE.USER_SUCCESS


def bl_get_nearest_cache_req(uid: int) -> list[str]:
    """
    Имя последних трех (или меньше) сохранённых запросов у пользователя с 'uid'.
    :param uid: Уникальный id пользователя.
    :return: Возвращает список названий последних сохранённых запросов.
    """
    reqs = DBCacheReq.get_nearest(uid)
    return [req.name for req in reqs]
