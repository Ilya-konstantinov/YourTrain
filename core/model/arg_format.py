from datetime import datetime, timedelta
from data.answer_enums import BAD_REQEST
from data.config import filter_dict, sort_dict, type_interp
import re


def time_arg(time: str) -> str | datetime:
    dep_time = datetime.now()
    try:
        if re.fullmatch(r'[+\-]\d+', time):  # For +del time
            dep_time += timedelta(minutes=int(time))
        elif time == '0':  # For no time changes
            ...
        elif re.fullmatch(r'[0-3]?[0-9]\.[0-1]?[0-9]', time):  # For DD.MM time, like 28.02
            dep_time = datetime.strptime(time, "%d.%m")
            dep_time = dep_time.replace(year=datetime.now().year)
        elif re.fullmatch(r'[0-3]?[0-9]\.[0-1]?[0-9]\.[0-9][0-9]', time):  # For DD.MM.YY time, like 14.11.06
            dep_time = datetime.strptime(time, "%d.%m.%y")
        elif re.fullmatch(r'[0-3]?[0-9]\.[0-1]?[0-9]\.20[0-2][0-9]', time):  # For DD.MM.YY time, like 14.11.2006
            dep_time = datetime.strptime(time, "%d.%m.%Y")
        elif re.fullmatch(r'[0-3]?[0-9]\.[0-1]?[0-9]\.[0-9][0-9]-[0-2]?[0-9]:[0-5][0-9]', time):  # For dd.mm.yy-HH:MM
            dep_time = datetime.strptime(time, "%d.%m.%y-%H.%M")
        elif re.fullmatch(r'[0-3]?[0-9]\.[0-1]?[0-9]\.20[0-2][0-9]-[0-2]?[0-9]:[0-5][0-9]',
                          time):  # For dd.mm.YYYY-HH:MM
            dep_time = datetime.strptime(time, "%d.%m.%Y-%H.%M")
        elif re.fullmatch(r'[0-2]?[0-9]:[0-5][0-9]', time):  # For HH:MM time, like 4:20
            tmp_time = datetime.strptime(time, "%H:%M")
            dep_time = dep_time.replace(hour=tmp_time.hour, minute=tmp_time.minute)
        else:
            return BAD_REQEST.BAD_TIME
    except:
        return BAD_REQEST.BAD_TIME

    return dep_time


def filter_arg(filter_type: str) -> int | str:
    for tp in filter_dict:
        if filter_type in tp:
            return filter_dict[tp]

    return BAD_REQEST.BAD_FILTER


def sort_arg(sort_type: str) -> int | str:
    for tp in sort_dict:
        if sort_type in tp:
            return sort_dict[tp]

    return BAD_REQEST.BAD_SORT


def param_arg(param: str) -> str:
    for tp in type_interp:
        if param in tp:
            return type_interp[tp]

    return SET.BAD_PARAM


def param_var(var: str) -> int:
    for tp in sort_dict:
        if var in tp:
            return sort_dict[tp]

    for tp in filter_dict:
        if var in tp:
            return filter_dict[tp]

    return var


def cor_name(name: str) -> bool:
    return re.fullmatch(r'[A-z_А-я0-9]+', name)
