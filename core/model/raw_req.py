import datetime
from datetime import datetime, timedelta

import requests

from data.config import Headers


def str_to_time(s: str) -> datetime:
    """
    Преобразует строку из формата времени запроса.
    :param s: Строка для формирования.
    :return: Время, которое вернул запрос.
    """
    timeobj = datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
    return timeobj


def date_to_delta(timeobj: datetime) -> timedelta:
    """
    Преобразует объект `datetime` в объект `timedelta` с соответствующими полями (hour, minute, second)
    :param timeobj: Объект для преобразования.
    :return: Объект `timedelta` преобразованный из `datetime`
    """
    return timedelta(hours=timeobj.hour, minutes=timeobj.minute, seconds=timeobj.second)


def get_path(dep_st_id: int, arr_st_id: int, date: datetime = datetime.today()) -> list | None:
    """
    Запрашивает полный путь по данному `id` станции отправления и прибытия у **API**.
    :param dep_st_id: `id` станции отправления.
    :param arr_st_id: `id` станции прибытия.
    :param date: Дата запроса.
    :return: Возвращает ответ API или None в случае, если ответа нет.
    """
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
    """
    Определяет станцию с самым похожим на входные данные названием. (на стороне **API**)
    :param station: Название искомой станции.
    :return: Возвращает None если ничего не найдено, или Json (Ответ API) в ином случае.
    """
    address = "https://backend.cppktrain.ru/train-schedule/search-station"
    params = {
        "query": station,
        "limit": 100
    }

    req = requests.get(address, params=params, headers=Headers)
    if req.status_code != 200 or req.text == "[]":
        return None  # TODO: что возвращать при нулевой станции

    raw_json = req.json()[0]
    return raw_json


def get_whole_path(pid: int) -> dict[int, tuple[timedelta, str, bool]] | None:
    """
    Обрабатывает весь маршрут с данным `path_id`.
    :param pid: Уникальный ``id`` маршрута.
    :return: Возвращает словарь станций, на которых останавливается данная электричка на этом маршруте в формате \
    station_id : (dep_time, station_name, is_skip)
    """
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
