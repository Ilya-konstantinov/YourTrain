import datetime

from core.data.answer_enums import CACHE_PATH
from core.database.dataframe import DB
from core.handler.req import bl_req, bl_mlt_req, ans_format
from core.model.raw_req import get_whole_path, date_to_delta
from threading import Timer
from datetime import timedelta
import schedule
user_cache_path: dict[int, list] = {}


async def cache_path(user_id: int, args: str) -> str:
    f = bl_req if args.find('--') == -1 else bl_mlt_req

    ans = await f(user_id=user_id, args=args, raw_ans=True)
    user_cache_path[user_id] = ans
    Timer(3*60, del_cache, args=[user_id])
    return ans_format(ans)


def del_cache(uid: int):
    if uid in user_cache_path.keys():
        user_cache_path.pop(uid)


async def num_path(user_id: int, args: str) -> str:
    try:
        num = int(args)
        num -= 1
    except:
        return CACHE_PATH.BAD_NUM

    if num >= len(user_cache_path[user_id]):
        user_cache_path.pop(user_id)
        return CACHE_PATH.BAD_NUM

    path = user_cache_path[user_id][num]
    user_cache_path.pop(user_id)

    if not DB.cache_path_create(user_id, path):
        return CACHE_PATH.ERROR

    return CACHE_PATH.SUCCESS


def refresh_whole_path():
    paths = DB.get_whole_cache_path()
    for path in paths:
        dep_time = get_whole_path(path['path_id'])[path['dep_st']][0]
        Timer(dep_time.seconds, refresh_path, args=[path['user_id'], path['path_id']])


def refresh_path(uid: int, pid: int):
    path_old = DB.get_one_cache_path(uid, pid)
    path_new = get_whole_path(path_old['path_id'])
    dep_time_old: timedelta = path_old['dep_time']
    dep_time_new: timedelta = timedelta(minutes= path_new['dep_time'].minute, hours= path_new['dep_time'].hour)
    delta = dep_time_new - dep_time_old
    changes: bool = False
    if abs(delta) > timedelta(seconds=1):
        changes = True
    dep_time_new_f = f'{dep_time_new.seconds // 3600}:{dep_time_new.seconds%3600//60:0>2}'
    to_dep_time = dep_time_new - date_to_delta(datetime.datetime.now())
    to_dep_time_f = f'{to_dep_time.seconds//60}'
    dep_st_f = DB.station_by_id(path_old['dep_st'])
    ans_ft = CACHE_PATH.MESSAGE_F.format(to_dep_time_f, dep_time_new_f, dep_st_f)
    if changes:
        status: str = 'раньше' if dep_time_new < timedelta(seconds=1) else 'позже'
        delta_f = f'{abs(delta).seconds//60}'
        ans_ft += CACHE_PATH.CHANGE_F(delta_f, status)

    # TODO как написать в чат лоху, если изменилось расписание


async def refr_sched() -> None:
    schedule.every().day.at("02:00").do(refresh_whole_path)
    schedule.run_pending()