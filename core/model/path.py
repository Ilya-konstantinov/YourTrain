from datetime import datetime, timedelta
from model.raw_req import get_whole_path
from data.config import sort_ind_to_rus, filter_ind_to_rus


class Station:
    """
    Класс станции
    """
    id: int
    title: str

    def __init__(self, id: int, title: str) -> None:
        self.id = id
        self.title = title


class Path:
    """
    Описывает маршрут
    Содержит поля: 
    path_id: int -- id маршрута
    dep_st: Station -- станция отправления маршрута
    arr_sr: Station -- станция прибытия маршрута
    start_st: Station -- станция начала маршрута
    finish_st: Station -- станция конца маршрута
    departure_time: datetime -- время отправления маршрута
    arrival_time: datetime -- время прибытия маршрута
    path_time: timedelta -- конкретное время маршрута 
    cost: int -- цена поездки
    high_speed: bool -- скоростной ли маршрут
    """

    def __init__(self, path_id: int,
                 dep_st: Station, arr_sr: Station,
                 start_st: Station, finish_st: Station,
                 departure_time: datetime, arrival_time: datetime,
                 cost: int, high_speed: bool) -> None:
        self.departure_time: datetime = departure_time

        self.arrival_time: datetime = arrival_time
        self.path_time: timedelta = (arrival_time - departure_time)
        self.path_id: int = path_id
        self.cost: int = int(cost)
        self.high_speed: bool = high_speed

        self.dep_st: Station = dep_st
        self.arr_st: Station = arr_sr
        self.start_st: Station = start_st
        self.finish_st: Station = finish_st

    def get_view(self) -> str:
        """Маршрут для отображения"""
        # Перобразование "сегодня" в datetime
        now = datetime.now()
        # Форматирование
        start_tile = beauty_station(self.start_st)
        finish_title = beauty_station(self.finish_st)
        dep_title = beauty_station(self.dep_st, 12)
        arr_tile = beauty_station(self.arr_st, 12)
        # строчка времени пути        
        st_time = f'{beauty_time(self.departure_time):<10}'
        path_time = f'{beauty_path_time(self.path_time):^10}'
        fn_time = f'{beauty_time(self.arrival_time):>10}'
        time = st_time + path_time + fn_time

        zero_line = f'{start_tile:<10}{" " * 10}{finish_title:>10}'
        second_line = f'{dep_title:<12}{" " * 6}{arr_tile:>12}'
        if self.departure_time >= now:
            third_line = f'Через {beauty_path_time(self.departure_time - now):^20}{self.cost:>3}р'
        else:
            return '\n'.join([zero_line, time, second_line])
        return '\n'.join([zero_line, time, second_line, third_line])

    def whole_path(self) -> list[str]:

        stops: list[tuple[str | bool]] = get_whole_path(self.path_id)
        for ind, st in enumerate(stops):
            stops[ind] = (
                f"{st[0]} {' ' * 4} {beauty_station(st[1])}",
                st[2]
            )

        return stops


class CacheRequest:
    """
    Параметры сохранённого запроса.
    """

    dep_sts: list[Station]
    arr_sts: list[Station]
    dep_time: datetime
    sort_type: int
    filter_type: int
    col: int
    is_mlt: bool
    name: str
    id: int

    def __init__(self, dep_st: list[Station], arr_st: list[Station], dep_time: datetime, filter_type: int,
                 sort_type: int, col: int, is_mlt: bool, id: int, name: str):
        """
        Создание класса сохранённого запроса.

        :param dep_st: Список станций отправления.
        :param arr_st: Список станций прибытия.
        :param dep_time: Время отсчета.
        :param sort_type: Тип сортировки.
        :param filter_type: Тип фильтрации.
        :param col: Количество станций на запросе.
        :param id: Уникальный `id` пути.
        :param name: Имя сохранённого пути.
        :param is_mlt: Является ли запрос мультистанцевыми.
        """
        self.dep_sts, self.arr_sts = dep_st, arr_st
        self.dep_time = dep_time
        if isinstance(self.dep_time, timedelta):
            self.dep_time = datetime.today().replace(hour=dep_time.seconds // 3600, minute=(dep_time.seconds % 3600) // 60)

        self.sort_type, self.filter_type, self.col, self.is_mlt = sort_type, filter_type, col, is_mlt
        self.id, self.name = id, name

    def get_view(self):
        title = f"{self.name:-^30}"
        dd = '-' * 30
        st_from = ', '.join([st.title.capitalize() for st in self.dep_sts])
        st_to = ', '.join([st.title.capitalize() for st in self.arr_sts])
        ans = [title, st_from, dd, st_to]
        if not (self.dep_time is None):
            dep_s = beauty_time(self.dep_time)
        else:
            dep_s = 'Любое'

        column_names = f'От{" " * 3}|Сортировка |Фильтр{" " * 4}|Кл'
        line = f'{dep_s:<5}|{sort_ind_to_rus[self.sort_type]:<10}|{filter_ind_to_rus[self.filter_type]:<10}|{self.col:<2}'
        ans += [column_names, dd, line]
        return '\n'.join(ans)

    def get_params(self, type = 0) -> str|tuple:
        dep_time = '0' if self.dep_time is None else beauty_time(self.dep_time)
        dep_time = dep_time.replace(":", '..')
        st_from = self.dep_sts[0].title.replace(' ', '_') if len(self.dep_sts) == 1 else [st.title.replace(' ', '_') for st in self.dep_sts]
        st_to = self.arr_sts[0].title.replace(' ', '_') if len(self.arr_sts) == 1 else [st.title.replace(' ', '_') for st in self.arr_sts]
        params = ' '.join([str(self.sort_type), str(self.filter_type), str(self.col)])
        if self.is_mlt:
            sts = st_from + ' -- ' + st_to
            return sts + '\n' + params
        else:
            sts = st_from + ' ' + st_to
            return sts + ' ' + params


def beauty_time(time: datetime) -> str:
    h = f'{time.hour:0>2}'
    m = f'{time.minute:0>2}'
    return f'{h}:{m}'


def beauty_path_time(path_time: datetime) -> str:
    """Конкретное время для отображения"""

    if isinstance(path_time, datetime):
        path_time = datetime(hours=path_time.hour, minutes=path_time.minute, seconds=path_time.second)

    path_time_view: str = ""
    if path_time.seconds >= 3600:
        path_time_view += f'{path_time.seconds // 3600} ч '
    path_time_view += f'{path_time.seconds % 3600 // 60} мин'

    return path_time_view


def beauty_station(st: Station, prefered_size: int = 10):
    """Станция для отображения"""
    st_tile = st.title.capitalize()
    st_tile = st_tile.replace('_', ' ').replace('-', ' ')
    st_tile = st_tile.split()[0]
    if len(st_tile) > prefered_size:
        st_tile = st_tile[:prefered_size - 1] + '.'
    return st_tile
