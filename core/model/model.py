from model.path import Station, Path
from datetime import datetime
import model.raw_req as raw_req
import json


def get_path(dep_st: Station, arr_st: Station, dep_time: datetime = datetime.now(), sort_type: int = 1,
             filter_type: int = 0, col: int = 10) -> list[Path]:
    raw_json = raw_req.get_path(dep_st.id, arr_st.id, dep_time)

    cur_list = list()

    for path in raw_json:
        if dep_time > raw_req.str_to_time(path["departureTime"]):
            continue
        is_speed: bool = not path["trainCategoryId"] == 4
        if is_speed and filter_type == 2:
            continue

        if not is_speed and filter_type == 1:
            continue


        cur_list.append(
            Path(
                path["scheduleId"],
                dep_st, arr_st,
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


def req(station_from: str, station_to: str, sort_type: int = 1, dep_time: datetime = datetime.now(),
        filter_type: int = 1, col: int = 10) -> list:
    if col <= 0:
        return []
    return get_path(get_station(station_from), get_station(station_to), dep_time=dep_time, sort_type=sort_type,
                    filter_type=filter_type, col=col)


def paths_sort(cur_list: list[Path], sort_type: int = 0) -> list[Path]:
    str_sort_type: str = "regular"
    with open("data/db_data.json") as f:
        js = json.load(f)
        str_sort_type = js['sort_type'][sort_type]

    cur_list = sorted(cur_list, key=lambda x: getattr(x, str_sort_type))
    return cur_list


def get_station(station: str) -> Station:
    raw_json = raw_req.get_station(station)
    return Station(
        raw_json["id"],
        raw_json["name"]
    )
