from datetime import timedelta, datetime
from raw_req import get_whole_path
class Station:
    """
    Класс станции
    Содержит поля:
    id: int -- id станции
    title: str -- название станции 
    """
    def __init__(self, id:int, title:str) -> None:
        self.id = id
        self.title = title


class Path:
    """
    Описывает маршрут
    Содержит поля: 
    path_id: int -- id маршрута
    dep_st: Station -- станция отпраления маршрута
    arr_sr: Station -- станция прибытия маршрута
    start_st: Station -- станция начала маршрута
    finish_st: Station -- станция конца маршрута
    departure_time: timedelta -- время отпраления маршрута
    arrival_time: timedelta -- время прибытия маршрута
    path_time: timedelta -- конкретное время маршрута 
    cost: int -- цена поездки
    high_speed: bool -- скоростной ли маршрут
    """
    def __init__(self, path_id: int, 
                 dep_st: Station, arr_sr: Station,
                 start_st: Station, finish_st: Station, 
                 departure_time: timedelta, arrival_time: timedelta, 
                 cost: int, high_speed: bool) -> None:
        self.departure_time: timedelta = departure_time
        # Если приезд на следующий день 
        # То для корректного вычисления времени
        # Добавляем день к дате прибытия 
        if (departure_time > arrival_time) :
            arrival_time += timedelta(minutes=0, days=1, microseconds=0, hours=0)
        
        self.arrival_time: timedelta = arrival_time
        self.path_time: timedelta = (arrival_time - departure_time)
        self.path_id: int = path_id
        self.cost: int = cost
        self.high_speed: bool = high_speed
        self.dep_st: Station = dep_st
        self.arr_st: Station = arr_sr
        self.start_st: Station = start_st
        self.finish_st: Station = finish_st
        
    
    def get_view(self) -> str:
        """Маршрут для отображения"""
        # Перобразование "сегодня" в timedelta
        now = datetime.now()
        now = timedelta(hours=now.hour, minutes=now.minute)
        # Форматирование
        start_tile = beauty_station(self.start_st)
        finish_title = beauty_station(self.finish_st)
        dep_title = beauty_station(self.dep_st, 12)
        arr_tile = beauty_station(self.arr_st, 12)
        # строчка времени пути        
        st_time = f'{beauty_time(self.departure_time):_<10}'
        path_time = f'{beauty_path_time(self.path_time):_^10}'
        fn_time = f'{beauty_time(self.arrival_time):_>10}'
        time = st_time + path_time + fn_time
        
        zero_line = f'{start_tile:_<10}{"_"*10}{finish_title:_>10}'
        second_line = f'{dep_title:_<12}{"-"*6}{arr_tile:_>12}'
        third_line = f'Через {beauty_path_time(self.departure_time - now )}'
        return '\n'.join([zero_line, time, second_line, third_line])
    
    def whole_path(self) -> list[str]:

        stops: list[tuple[str|bool]] = get_whole_path(self.path_id)
        for ind, st in enumerate(stops):
            stops[ind] = (
                            f"{st[0]} {'-'*4} {beauty_station(st[1])}",
                            st[2]
                        )

        return stops
    
def beauty_time(time: timedelta) -> str:
    h = f'{time.seconds//3600:0>2}'
    m = f'{time.seconds%3600//60:0>2}'
    return f'{h}:{m}'

def beauty_path_time(path_time: timedelta) -> str:
    """Конкретное время для отображения"""
    
    if isinstance(path_time,datetime):
        path_time = timedelta(hours=path_time.hour, minutes=path_time.minute, seconds=path_time.second)
    
    path_time_view: str = ""
    if (path_time.seconds >= 3600):
        path_time_view += f'{path_time.seconds//3600} ч '
    path_time_view += f'{path_time.seconds%3600//60} мин'
    
    return path_time_view

def beauty_station(st: Station, prefered_size: int = 10):
    """Станция для отображение"""
    st_tile = st.title.capitalize()
    st_tile = st_tile.replace('_', ' ').replace('-', ' ')
    st_tile = st_tile.split()[0]
    if (len(st_tile) > prefered_size):
        st_tile = st_tile[:prefered_size-1] + '.'
    return st_tile

