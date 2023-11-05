import json
import datetime
from datetime import datetime, time, timedelta, date
import requests
from data.config import Headers


def str_to_time(s: str) -> datetime:
    timeobj = datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
    return timeobj


def date_to_delta(timeobj: datetime) -> timedelta:
    return timedelta(hours=timeobj.hour, minutes=timeobj.minute, seconds=timeobj.second)


def get_path(dep_st_id: int, arr_st_id: int, date: datetime = datetime.today()) -> list | None:
    address = "https://backend.cppktrain.ru/train-schedule/date-travel"

    params = {
        "fromStationId": dep_st_id,
        "toStationId": arr_st_id,
        "date": date.strftime("%Y-%m-%d")
    }

    req = requests.get(address, params=params, headers=Headers)

    if req.status_code != 200:
        return None  # TODO: что возвращать при сломанном рейсе

    raw_json = req.json()
    return raw_json


def get_station(station: str):
    address = "https://backend.cppktrain.ru/train-schedule/search-station"
    params = {
        "query": station,
        "limit": 100
    }

    req = requests.get(address, params=params, headers=Headers)
    # station = station.replace('_', ' ').replace('-', ' ')
    if req.status_code != 200 or req.text == "[]":
        return None  # TODO: что возвращать при нулевой станции

    raw_json = req.json()[0]
    return raw_json


def get_whole_path(pid: int) -> dict[int, tuple[timedelta | str | bool]] | None:
    address: str = "https://backend.cppktrain.ru/train-schedule/schedule/{}"

    address = address.format(pid)

    params: dict = {
        "date": datetime.now().strftime("%Y-%m-%d")
    }

    req = requests.get(url=address, params=params, headers=Headers)

    if req.status_code != 200:
        return None  # TODO: что возвращать при не срабатывании

    raw_json = req.json()

    stops_st = {}
    for st in raw_json["stops"]:
        st_tuple = {
            st['station']["expressId"]:
                (
                date_to_delta(datetime.strptime(st["departureTime"], "%Y-%m-%dT%H:%M:%S")),
                st["station"]["name"],
                st["skip"]
                )
            }
        stops_st.update(st_tuple)

    return stops_st

