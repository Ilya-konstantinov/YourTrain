from datetime import datetime, timedelta

from data.config import sort_ind_to_rus, filter_ind_to_rus

"""
Все функции .get_view() ограничены длинной 30 символов в длину, ради улучшения восприятия на маленьких экранах телефона.
"""


class Station:
    """
    Класс станции
    """
    id: int  # Уникальный id станции
    title: str  # Название станции

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
                 dep_time: datetime, arrival_time: datetime,
                 cost: int, high_speed: bool) -> None:
        self.dep_time: datetime = dep_time

        self.arr_time: datetime = arrival_time
        self.path_time: timedelta = (arrival_time - dep_time)
        self.path_id: int = path_id
        self.cost: int = int(cost)
        self.high_speed: bool = high_speed

        self.dep_st: Station = dep_st
        self.arr_st: Station = arr_sr
        self.start_st: Station = start_st
        self.finish_st: Station = finish_st

    def get_view(self) -> str:
        """Маршрут для отображения"""
        # Прeобразование "сегодня" в datetime
        now = datetime.now()
        # Форматирование
        start_tile = beauty_station(self.start_st)
        finish_title = beauty_station(self.finish_st)
        dep_title = beauty_station(self.dep_st, 12)
        arr_tile = beauty_station(self.arr_st, 12)
        # строчка времени пути        
        st_time = f'{beauty_time(self.dep_time):<10}'
        path_time = f'{beauty_path_time(self.path_time):^10}'
        fn_time = f'{beauty_time(self.arr_time):>10}'
        time = st_time + path_time + fn_time

        zero_line = f'{start_tile:<10}{" " * 10}{finish_title:>10}'
        second_line = f'{dep_title:<12}{" " * 6}{arr_tile:>12}'
        if self.dep_time >= now:
            third_line = f'Через {beauty_path_time(self.dep_time - now):^20}{self.cost:>3}р'
        else:
            return '\n'.join([zero_line, time, second_line])
        return '\n'.join([zero_line, time, second_line, third_line])


class CachePath:
    """
    Класс закешированного маршрута.
    """
    path_id: int
    user_id: int
    dep_st: Station
    arr_st: Station
    dep_time: timedelta
    only_updates: bool

    def __init__(self, dep_st: Station, arr_st: Station, dep_time: timedelta, path_id: int, user_id: int,
                 only_updates: bool):
        self.dep_st, self.arr_st = dep_st, arr_st
        self.dep_time, self.only_updates = dep_time, only_updates
        self.path_id, self.user_id = path_id, user_id

    def get_view(self) -> str:
        """
        Отображение маршрута.
        :return: Возвращает отображение маршрута.
        """
        dep_time = datetime.today().replace(hour=self.dep_time.seconds // 3600,
                                            minute=(self.dep_time.seconds % 3600) // 60)
        dep_time_f = f'Время отбытия: {beauty_time(dep_time)}'
        dep_title = beauty_station(self.dep_st, 12)
        arr_tile = beauty_station(self.arr_st, 12)
        second_line = f'{dep_title:<12}{" " * 6}{arr_tile:>12}'
        return '\n'.join([dep_time_f, second_line])


class CacheRequest:
    """
    Параметры сохранённого запроса.
    """

    dep_st: list[Station]
    arr_st: list[Station]
    dep_time: str
    sort_type: int
    filter_type: int
    col: int
    is_mlt: bool
    name: str | None
    user_id: int | None

    def __init__(self, dep_st: list[Station], arr_st: list[Station], dep_time: str = '0', sort_type: int = 0,
                 filter_type: int = 0, col: int = 5, is_mlt: bool = 0, user_id: int = None, name: str = None):
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
        self.dep_st, self.arr_st = dep_st, arr_st
        self.dep_time = dep_time

        if isinstance(self.dep_time, timedelta):
            self.dep_time = datetime.today().replace(hour=dep_time.seconds // 3600,
                                                     minute=(dep_time.seconds % 3600) // 60)

        self.sort_type, self.filter_type, self.col, self.is_mlt = sort_type, filter_type, col, is_mlt
        self.user_id, self.name = user_id, name

        if len(dep_st) > 1 or len(arr_st) > 1:
            self.is_mlt = 1

    def get_view(self) -> str:
        """
        Отображение сохранённого запроса.
        :return: Отображение сохранённого запроса.
        """
        title = f"{self.name:-^30}"
        dd = '-' * 30
        st_from = ', '.join([st.title.capitalize() for st in self.dep_st])
        st_to = ', '.join([st.title.capitalize() for st in self.arr_st])
        ans = [title, st_from, dd, st_to, dd]

        dep_s = self.dep_time
        if dep_s in [None, '-', 0, '0']:
            dep_s = 'Любое'

        column_names = f'От{" " * 3}|Сортировка|Фильтр{" " * 4}|Кл'
        line = f'{dep_s:<5}|{sort_ind_to_rus[self.sort_type]:<10}|{filter_ind_to_rus[self.filter_type]:<10}|{self.col:<2}'
        ans += [column_names, dd, line]
        return '\n'.join(ans)

    def get_params(self) -> str | tuple:
        """
        Возвращает параметры сохранённого запроса в виде строки
        "dep_st_id arr_st_id dep_time sort_type filter_type col".
        """
        st_from = str(self.dep_st[0].id) \
            if len(self.dep_st) == 1 else \
            ' '.join([str(st.id) for st in self.dep_st])

        st_to = str(self.arr_st[0].id) \
            if len(self.dep_st) == 1 else \
            ' '.join([str(st.id) for st in self.arr_st])

        dep_time: str = '0' if self.dep_time is None else self.dep_time
        dep_time: str = dep_time.replace(":", '..')
        params = ' '.join([dep_time, str(self.sort_type), str(self.filter_type), str(self.col)])

        if self.is_mlt:
            sts = st_from + ' -- ' + st_to
            return sts + '\n' + params
        else:
            sts = st_from + ' ' + st_to
            return sts + ' ' + params


def beauty_time(time: datetime) -> str:
    """
    Преобразует `time` в строку формата HH:MM.
    :param time: Объект `datetime` для преобразования.
    :returns: Возвращает строку формата HH:MM.
    """
    h = f'{time.hour:0>2}'
    m = f'{time.minute:0>2}'
    return f'{h}:{m}'


def beauty_path_time(path_time: datetime | timedelta) -> str:
    """Конкретное время для отображения"""
    if isinstance(path_time, datetime):
        path_time = timedelta(hours=path_time.hour, minutes=path_time.minute, seconds=path_time.second)

    path_time_view: str = ""
    if path_time.seconds >= 3600:
        path_time_view += f'{path_time.seconds // 3600} ч '
    path_time_view += f'{path_time.seconds % 3600 // 60} мин'

    return path_time_view


def beauty_station(st: Station, preferred_size: int = 10):
    """Станция для отображения"""
    st_tile = st.title.capitalize()
    st_tile = st_tile.replace('_', ' ').replace('-', ' ')
    st_tile = st_tile.split()[0]
    if len(st_tile) > preferred_size:
        st_tile = st_tile[:preferred_size - 1] + '.'
    return st_tile
