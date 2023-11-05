import json
from datetime import datetime, timedelta

import model.raw_req as raw_req
from model.path import Station, Path


def get_path(dep_st: Station, arr_st: Station, dep_time: datetime = datetime.now(), sort_type: int = 1,
             filter_type: int = 0, col: int = 10) -> list[Path]:
    """
    Обрабатывает запрос API на расписание электричек от станции до станции.
    :param dep_st: Станция отправления.
    :param arr_st: Станция прибытия.
    :param dep_time: Время отбытия в формате datetime или None.
    :param sort_type: Тип сортировки от 0 до 2.
    :param filter_type: Тип фильтрации от 0 до 2.
    :param col: Количество электричек в запросе.
    :return: Список путей в формате list[path.Path]
    """
    if dep_time is None:
        dep_time = datetime.now()
    if isinstance(dep_time, timedelta):
        dep_time = datetime.today().replace(hour=dep_time.seconds // 3600, minute=(dep_time.seconds % 3600) // 60)

    raw_json = raw_req.get_path(dep_st.id, arr_st.id, dep_time)

    cur_list = list()
    for path in raw_json:

        if dep_time > raw_req.str_to_time(path["departureTime"]):
            continue

        is_speed: bool = not path["trainCategoryId"] == 4

        if (is_speed and filter_type == 2) or (not is_speed and filter_type == 1):
            continue

        cur_list.append(
            Path(
                path["scheduleId"],
                Station(path["departureStationId"], path["departureStationName"]),
                Station(path["arrivalStationId"], path["arrivalStationName"]),
                Station(path['startStationId'], path['startStationName']),
                Station(path['finishStationId'], path["finishStationName"]),
                raw_req.str_to_time(path["departureTime"]), raw_req.str_to_time(path["arrivalTime"]),
                path["cost"], is_speed
            )
        )

        if len(cur_list) >= col and len(cur_list) >= 5:
            break

    cur_list = paths_sort(cur_list, sort_type)

    return cur_list[:col]


def req(station_from: str, station_to: str, sort_type: int = 0, dep_time: datetime = datetime.now(),
        filter_type: int = 0, col: int = 10) -> list[Path]:
    """
    Возвращает запрос на рассписание от станции до станции в формате списка путей.
    :param station_from: Название станции отправления.
    :param station_to: Название станции прибытия.
    :param dep_time: Время отбытия в формате datetime или None.
    :param sort_type: Тип сортировки от 0 до 2.
    :param filter_type: Тип фильтрации от 0 до 2.
    :param col: Количество электричек в запросе.
    :return: Список путей в формате list[path.Path]
    """
    if col <= 0:
        return []
    if isinstance(station_from, Station) and isinstance(station_to, Station):
        return get_path(dep_st=station_from, arr_st=station_to, dep_time=dep_time, sort_type=sort_type,
                        filter_type=filter_type, col=col)
    return get_path(get_station(station_from), get_station(station_to), dep_time=dep_time, sort_type=sort_type,
                    filter_type=filter_type, col=col)


def paths_sort(cur_list: list[Path], sort_type: int = 0) -> list[Path]:
    """
    Сортирует список путей по `sort_type`
    :param cur_list: Список путей (объект типа path.Path)
    :param sort_type: Тип сортировки от 0 до 2 в соответсвии с "data/db_data.json"
    :return: Возращает отсортированный список.
    """
    str_sort_type: str = "regular"
    with open("data/db_data.json") as f:
        js = json.load(f)
        str_sort_type = js['sort_type'][sort_type]

    cur_list = sorted(cur_list, key=lambda x: getattr(x, str_sort_type))
    return cur_list


def get_station(station: str) -> Station | None:
    """
    Преобразует станцию по имени в объект класса Station.
    :param station: Имя станции.
    :return: Возвращает объект станции, если такая есть, в ином случае None.
    """
    raw_json = raw_req.get_station(station)
    return Station(
        raw_json["id"],
        raw_json["name"]
    ) if raw_json else raw_json
