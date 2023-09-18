from datetime import datetime, timedelta
from core.data.answer_enums import *
import re

sort_dict = {
    ('dpt', 'departure_time', '0'): 0,
    ('1', 'arrival_time', 'art'): 1,
    ('2', 'path_time', 'pht'): 2,
}

filter_dict = {
    ("all", '0'): 0,
    ("1", 'speed', 'sd'): 1,
    ('2', 'rg'): 2,
}


def time_arg(time: str, dep_time: datetime) -> str | datetime:
    if re.fullmatch(r'[+\-]\d+', time):  # For +del time
        dep_time += timedelta(minutes=int(time))
    elif time == '0':  # For no time changes
        ...
    elif re.fullmatch(r'[0-3]?[0-9]\.[0-1]?[0-9]', time):  # For DD.MM time, like 28.02
        try:
            dep_time = datetime.strptime(time, "%d.%m")
            dep_time = dep_time.replace(year=datetime.now().year)
        except:
            return BAD_REQEST.BAD_TIME
    elif re.fullmatch(r'[0-3]?[0-9].[0-1]?[0-9]\.[0-9][0-9]', time):  # For DD.MM.YY time, like 14.11.06
        try:
            dep_time = datetime.strptime(time, "%d.%m.%y")
        except:
            return BAD_REQEST.BAD_TIME
    elif re.fullmatch(r'[0-3]?[0-9]\.[0-1]?[0-9]\.20[0-2][0-9]', time):  # For DD.MM.YY time, like 14.11.2006
        try:
            dep_time = datetime.strptime(time, "%d.%m.%Y")
        except:
            return BAD_REQEST.BAD_TIME
    elif re.fullmatch(r'[0-3]?[0-9]\.[0-1]?[0-9]\.[0-9][0-9]-[0-2]?[0-9]\.[0-5][0-9]', time):  # For dd.mm.yy-HH.MM
        try:
            dep_time = datetime.strptime(time, "%d.%m.%y-%H.%M")
        except:
            return BAD_REQEST.BAD_TIME
    elif re.fullmatch(r'[0-3]?[0-9]\.[0-1]?[0-9]\.20[0-2][0-9]-[0-2]?[0-9]\.[0-5][0-9]', time):  # For dd.mm.YYYY-HH.MM
        try:
            dep_time = datetime.strptime(time, "%d.%m.%Y-%H.%M")
        except:
            return BAD_REQEST.BAD_TIME
    elif re.fullmatch(r'[0-2]?[0-9]\.[0-5][0-9]', time):  # For HH.MM time, like 4.20
        tmp_time = datetime.strptime(time, "%H.%M")
        dep_time = dep_time.replace(hour=tmp_time.hour, minute=tmp_time.minute)
    elif re.fullmatch(r'[0-2]?[0-9]:[0-5][0-9]', time):  # For HH:MM time, like 4:20
        tmp_time = datetime.strptime(time, "%H:%M")
        dep_time = dep_time.replace(hour=tmp_time.hour, minute=tmp_time.minute)
    else:
        return BAD_REQEST.BAD_TIME

    return dep_time


def filter_arg(filter_type: str) -> int | str:
    for tp in filter_dict:
        if filter_type in tp:
            return filter_dict[tp]

    return BAD_REQEST.BAD_FILTER


def sort_arg(sort_type: str) -> int | str:
    for tp in sort_dict:
        if (sort_type in tp):
            return sort_dict[tp]

    return BAD_REQEST.BAD_SORT
