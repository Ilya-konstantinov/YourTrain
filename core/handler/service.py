from data.answer_enums import HELP, SET, COMMENT, DEL_INFO, RECACHE
from database.dataframe import DB
from model.arg_format import param_arg, param_var, type_interp, cor_name, sort_dict


async def bl_start(user_id: int, user_exists: bool):
    user_name = DB.user_params(user_id)[0]
    if user_exists:
        return HELP.START_OLD_F.format(user_name)
    else:
        return HELP.START_NEW_F.format(user_name)


async def bl_help(user_id: int, args: str):
    user_name = DB.user_params(user_id)[0]
    match args:
        case None:
            return HELP.BASE_F.format(user_name)
        case "req":
            return HELP.REQ
        case _:
            return HELP.BASE_F.format(user_name)


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

    return SET.SUCCESS_F.format(args[0], args[1])


async def bl_del_user_info(uid: int, name: str) -> str:
    """
    Удаляет информацию о пользователе.

    :param name: Имя пользователя.
    :param uid: Уникальный id пользователя.
    :return: Возвращает сообщение SUCCESS в случае успеха, UNSUCCESSFUL иначе.
    """

    is_suc = DB.del_info(uid, name)
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
    try:
        DB.recache_user(uid, name)
    except:
        return RECACHE.USER_ERROR

    return RECACHE.USER_SUCCESS

