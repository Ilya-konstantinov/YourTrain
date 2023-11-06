import asyncio
import datetime
from datetime import timedelta

import aioschedule
import schedule

from data.answer_enums import CACHE_PATH
from database.db_cache_path import DBCachePath
from database.db_recache import DBRecache
from keyboard.cache_path import path_inline
from logic.req import bl_req, bl_mlt_req, ans_format
from model import model
from model.path import CachePath, Path
from model.raw_req import get_whole_path, date_to_delta


async def cache_path(user_id: int, args: str) -> str | tuple:
    """
    Дать пользователю выбор маршрута из запроса с данными параметра.

    :param user_id: Уникальный id пользователя
    :param args: Параметры запроса [sort_type[, filter_type[, col[, dep_time]]]]
    :return: Возвращает текст запроса если он выполнен, текст ошибки иначе.
    """
    f = bl_req if args.find('--') == -1 else bl_mlt_req

    ans = await f(user_id=user_id, args=args, raw_ans=True)
    if isinstance(ans, str):
        return ans
    return ans_format(ans), ans


def refresh_whole_path(bot) -> None:
    """
    Распределяет все запросы в расписание отправки сообщений.
    :param bot: Бот, от лица которого будут засылаться ответы.
    """
    aioschedule.clear()
    paths: list[CachePath] = DBCachePath.get_whole_cache_path()
    for path in paths:
        dep_time = path.dep_time
        aioschedule.every().day.at(f'{dep_time.seconds // 3600}:{dep_time.seconds % 3600 // 60}').do(
            refresh_path,
            bot=bot, path_old=path
        )
        # aioschedule.every(7).seconds.do(refresh_path, bot=bot, path_old=path)


async def refresh_path(bot, path_old: CachePath):
    """
    Обновление пути и отправка пользователю сообщения о прибытие данного поезда.
    :param bot: Бот, от лица которого будут засылаться ответы.
    :param path_old: Путь, который необходимо обработать
    """
    path_new = get_whole_path(path_old.path_id)
    if path_new is None:
        path_old = await recache_path(path_old)
        path_new = get_whole_path(path_old.path_id)
    dep_time_old: timedelta = path_old.dep_time
    dep_time_new: timedelta = path_new[path_old.dep_st.id][0]
    delta = dep_time_new - dep_time_old
    changes: bool = False

    if abs(delta) > timedelta(minutes=1):
        changes = True

    dep_time_new_f = f'{dep_time_new.seconds // 3600}:{dep_time_new.seconds % 3600 // 60:0>2}'
    to_dep_time = dep_time_new - date_to_delta(datetime.datetime.now())
    to_dep_time_f = f'{to_dep_time.seconds // 60}'
    dep_st_f = path_old.dep_st.title
    ans = CACHE_PATH.MESSAGE_F.format(to_dep_time_f, dep_time_new_f, dep_st_f)

    if changes:
        status: str = 'раньше' if dep_time_new < timedelta(seconds=1) else 'позже'
        delta_f = f'{abs(delta).seconds // 60}'
        ans += CACHE_PATH.CHANGE_F.format(delta_f, status)
        await recache_path(path_old)

    await bot.send_message(path_old.user_id, ans, reply_markup=path_inline(
        path_old.path_id, path_old.user_id
    ))
    return aioschedule.CancelJob


async def recache_path(path_old) -> CachePath:
    """
    Полное обновление пути на случай изменение его в **API**.
    :param path_old: Старая версия пути.
    :return: Новый путь.
    """
    dep_st = path_old.dep_st
    arr_st = path_old.arr_st
    dep_time: datetime = path_old.dep_time
    paths: list[Path] = model.req(station_from=dep_st, station_to=arr_st, dep_time=(dep_time - timedelta(minutes=5)))
    for ind, path in enumerate(paths):
        path.dep_time = timedelta(hours=path.dep_time.hour, minutes=path.dep_time.minute)
        paths[ind] = path

    paths.sort(key=lambda x: abs(dep_time - x.dep_time))
    path: Path = paths[0]
    path: CachePath = CachePath(
        dep_st=path.dep_st, arr_st=path.arr_st,
        dep_time=path.dep_time, path_id=path.path_id,
        user_id=path_old.user_id, only_updates=path_old.only_updates
    )
    DBRecache.recache_path(path_old, path)
    return path


async def refr_sched(bot) -> None:
    """
    Установка времени распределения расписания и "ловля" процессов расписания.
    :param bot: Бот, от лица которого будут засылаться ответы.
    """
    schedule.every().day.at("02:00").do(refresh_whole_path, bot=bot)
    # schedule.every(10).seconds.do(refresh_whole_path, bot=bot)
    while True:
        schedule.run_pending()
        await aioschedule.run_pending()
        await asyncio.sleep(1)


def bl_path_view(uid: int) -> str:
    """
    Запрос на отображение всех сохранённых маршрутов.
    :param uid: Уникальный id пользователя.
    :return: Отображение всех сохранённых маршрутов пользователя в формате MARKDOWN_2.
    """
    paths = DBCachePath.get_users_cache_path(uid)
    return f'`{"-" * 30}`\n'.join([
        f'```\n{path.get_view()}\n```' for path in paths
    ])
