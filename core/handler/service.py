from core.data.answer_enums import HELP, SET
from core.database.dataframe import DB
from core.model.arg_format import param_arg, param_var, type_interp, cor_name, sort_dict


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
