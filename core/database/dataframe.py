from typing import Tuple

from mysql.connector import connect
from data.config import DB_DATA, DB_DEFAULT
from datetime import datetime, timedelta
from model.path import Station, Path
import json


class DataBase:
    """
    Класс для связи с БД.
    """

    def __init__(self):
        """
        Инициализация связи с БД
        согласно config.DB_DATA.
        """
        self.cnx = connect(**DB_DATA)
        self.cur = self.cnx.cursor()
        self.cnx.autocommit = True

    # <-------------------------------------------------USER_EDIT------------------------------------------------->

    def user_create(
            self, uid: int,
            name: str,
            chat_id: int
    ) -> bool:
        """
        Создание user.

        :param uid: `id` пользователя.
        :param name: Обращение к пользователю.
        :param chat_id: `id` часа с пользователем.
        :returns: Возвращает True, если удается создать нового юзера, False если не получается.
        """
        if self.user_exist(uid):
            return False

        qer = "INSERT INTO users (id, name, chat_id, filter_type, sort_type, col) VALUES (%s, %s, %s, %s, %s, %s);"
        self.cur.execute(qer, (uid, name, chat_id, *DB_DEFAULT))
        return True

    def user_exist(self, uid: int) -> bool:
        """
        Проверка существует ли пользователь с заданным id.

        :param uid: Уникальный id пользователя.
        :returns: Возвращает True если пользователь существует, иначе False.
        """
        qer = "SELECT name FROM users WHERE id = %s"
        self.cur.execute(qer, [uid])
        return not (self.cur.fetchone() is None)

    def user_params(self, uid: int) -> tuple[str | int] | bool:
        """
        Возвращает параметры по умолчанию для user.

        :param uid: Уникальный id пользователя.
        :returns: Возвращает (name, sort_type, filter_type, col) если пользователь есть, иначе False.
        """
        if not self.user_exist(uid):
            return False
        qer = "SELECT name, sort_type, filter_type, col FROM users WHERE id = %s;"
        self.cur.execute(qer, tuple([uid]))
        return self.cur.fetchone()

    def set_params(self, uid: int, param_key: str, param_val: int) -> bool:
        """
        Изменяет параметр по умолчанию для user

        :param uid: Уникальный id пользователя.
        :param param_key: Имя параметра, который необходимо изменить.
        :param param_val: Значение, на которое изменяется параметр.
        :returns: True если успешное изменение, False если нет такого user.
        """
        if not self.user_exist(uid):
            return False
        qer = f"UPDATE users SET {param_key} = %s WHERE id = %s;"
        params = (param_val, uid)
        self.cur.execute(qer, params)
        return True

    # <-------------------------------------------------USER_EDIT------------------------------------------------->
    # <-------------------------------------------------CACHE_REQ------------------------------------------------->

    def cache_req_col(self, uid: int) -> int:
        """
        Количество сохранённых запросов у пользователя.

        :param uid: Уникальный id пользователя.
        :returns:  Количество сохранённых запросов у пользователя.
        """
        qer = 'SELECT number FROM req_cache WHERE user_id = %s ORDER BY number DESC LIMIT 1;'
        params = [uid]
        self.cur.execute(qer, params)
        ans = self.cur.fetchone()

        return ans[0]

    def cache_req_exists(self, uid: int, identification: str | int) -> bool:
        """
        Проверка существует ли пользователь с заданным id.

        :param uid: Уникальный id пользователя.
        :param identification: Опознавательный признак сохранённого запроса.
        :return: Возвращает True если запрос существует, иначе False.
        """
        column_title = ('name' if isinstance(identification, str) else 'number')
        qer = f"SELECT * FROM req_cache WHERE {column_title} = %s AND user_id = %s;"
        params = [identification, uid]
        self.cur.execute(qer, params)
        return not (self.cur.fetchone() is None)

    def cache_req_create(self, uid: int, name: str, dep_st_id: list[int], arr_st_id: list[int], sort_type: int,
                         filter_type: int, col: int, is_mlt: bool, dep_time: datetime) -> bool:
        """
        Сохраняет электричку с данными параметрами в БД.

        :param uid: Уникальный id пользователя.
        :param is_mlt: Является ли
        :param col: Количество электричек в запросе.
        :param filter_type: Тип фильтрации.
        :param sort_type: Тип сортировки.
        :param arr_st_id: Список станций прибытия.
        :param dep_st_id: Список станций отправления.
        :param name: Имя сохранённого запроса.
        :param dep_time: Время отбытия.
        :returns: Возвращает True если за спрос сохранён и False если сохранить запрос не получилось
        """
        if self.cache_req_exists(uid, name):
            return False
        req_col: int = self.cache_req_col(uid) + 1
        qer: str = ("INSERT INTO req_cache (dep_st_id, arr_st_id, sort_type, filter_type, "
                    "dep_time, is_mlt, user_id, name, number, col) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);")

        if datetime.now() - dep_time <= timedelta(seconds=10):
            dep_time = None

        dep_st_id: str = '[' + ','.join([str(i) for i in dep_st_id]) + ']'
        arr_st_id: str = '[' + ','.join([str(i) for i in arr_st_id]) + ']'
        params = (dep_st_id, arr_st_id, sort_type, filter_type, dep_time, is_mlt, uid, name, req_col, col)
        self.cur.execute(qer, params)
        return True

    def cache_req_get(self, uid: int, identification: str | int) -> bool | tuple[str, str, bool]:
        """
        Возвращает параметры для сохранённого запроса.
        :param uid: Уникальный id пользователя.
        :param identification: Опознавательный признак сохранённого запроса.
        :returns:
          Возвращает параметры запроса в формате.
         * (список станций отправления, станций прибытия)
         * (время прибытия, тип сортировки, тип фильтра, количество электричек)
         * (несколько ли станций отправления/прибытия)
        :type: bool | tuple[str, str, bool]
        """
        identification = ind_format(identification)

        if not self.cache_req_exists(uid, identification):
            return False

        column_title = ('name' if isinstance(identification, str) else 'number')
        qer = (f"SELECT dep_st_id, arr_st_id, dep_time, sort_type, filter_type, col, is_mlt FROM req_cache "
               f"WHERE {column_title} = %s AND user_id = %s;")
        params = [identification, uid]
        self.cur.execute(qer, params)
        ans = list(self.cur.fetchone())
        dep_time, sort_type, filter_type, col = ans[2:-1]

        if dep_time is None:
            dep_time = datetime.now()
        else:
            dep_time = datetime.today().replace(hour=dep_time.seconds // 3600, minute=(dep_time.seconds % 3600) // 60)

        is_mlt: bool = bool(ans[-1])
        dep_st_id, arr_st_id = ans[:2]
        dep_st_id, arr_st_id = json.loads(dep_st_id), json.loads(arr_st_id)

        for ind, st in enumerate(dep_st_id):
            dep_st_id[ind] = self.station_by_id(st)

        for ind, st in enumerate(arr_st_id):
            arr_st_id[ind] = self.station_by_id(st)

        return (dep_st_id, arr_st_id), (dep_time, sort_type, filter_type, col), is_mlt

    # <-------------------------------------------------CACHE_REQ------------------------------------------------->
    # <-----------------------------------------------CACHE_STATION----------------------------------------------->

    def station_by_id(self, st_id: int) -> str | bool:
        """
        Возвращает имя станции по её названию.

        :param st_id: `id` станции.
        :returns: False если такой станции нет, её название если есть.
        """
        if not self.station_exists(st_id):
            return False
        qer = "SELECT title FROM station_cache WHERE id = %s"
        params = [st_id]
        self.cur.execute(qer, params)
        return self.cur.fetchone()[0]

    def station_create(self, st: Station):
        """
        Создает станцию.

        :param st: Станция, которую надо создать.
        :return: Создает станцию. Если такая станция существует, то ничего не делает
        """
        qer = "INSERT INTO station_cache (id, title) VALUES (%s, %s);"
        params = [st.id, st.title]
        try:
            self.cur.execute(qer, params)
        except:
            return

    def station_exists(self, st: Station):
        """
        Проверяет, существует ли станция.

        :param st: Станция, которая идет на проверку.
        :return: True если станция существует, False в ином случае.
        """
        qer = "SELECT * FROM station_cache WHERE id = %s"
        params = [st.id]
        self.cur.execute(qer, params)
        return not (self.cur.fetchone() is None)
    # <-----------------------------------------------CACHE_STATION----------------------------------------------->
    # <-------------------------------------------------PATH_CACHE------------------------------------------------->
    def path_exists(self, uid: int, pid: int) -> bool:
        """
        Проверяет, существует ли такой сохранённый маршрут у пользователя.
        :param uid: Уникальный id пользователя.
        :param pid: `id` пути.
        :return: True если маршрут есть у этого пользователя, False в ином случае.
        """
        qer = "SELECT * FROM path_cache WHERE user_id = %s and path_id = %s"
        params = [uid, pid]
        self.cur.execute(qer, params)
        return not (self.cur.fetchone() is None)

    def cache_path_create(self, uid: int, path: Path):
        """
        Сохраняет маршрут пользователю.

        :param uid: Уникальный id пользователя.
        :param path: Путь, который необходимо добавить.
        :return: Возвращает False, если станцию создать не удалось.
        """

        if self.path_exists(uid, path.path_id):
            return False
        try:
            qer = ("INSERT INTO path_cache(path_id, user_id, dep_st, arr_st, dep_time) "
                   "VALUES (%s, %s, %s, %s, %s)")
            params = [path.path_id, uid, path.dep_st.id, path.arr_st.id, path.departure_time]
            self.cur.execute(qer, params)
        except:
            return False
        return True

    def cache_path_get(self, uid: int, path: int) -> tuple[Station, Station, datetime] | bool:
        """
        Возвращает параметры для запроса к API сохранённого маршрута.

        :param uid: Уникальный id пользователя.
        :param path: `id` пути, который надо вернуть.
        :return: Возвращает параметры для запроса в формате
        (Станция отправления, станция прибытия, время старое отправления)
        """
        if not self.path_exists(uid, path):
            return False

        qer = "SELECT dep_st, arr_st, dep_time FROM path_cache WHERE user_id = %s AND path_id = %s"
        params = [uid, path]
        self.cur.execute(qer, params)
        dep_st, arr_st, dep_time = self.cur.fetchone()
        dep_st, arr_st = (
            Station(
                id=dep_time,
                title=self.station_by_id(dep_st)
            ),
            Station(
                id=arr_st,
                title=self.station_by_id(arr_st)
            )
        )
        dep_time = datetime.today().replace(hour=dep_time.seconds // 3600, minute=(dep_time.seconds % 3600) // 60)

        return dep_st, arr_st, dep_time

    @property
    def get_whole_cache_path(self) -> list[dict[str,]]:
        """
        Возвращает все сохранённые маршруты.
        :return: Список в формате (Станция отправления, станция прибытия, время старое отправления).
        """
        qer = "SELECT path_id, user_id, dep_st, arr_st, dep_time FROM path_cache;"
        keys = ["path_id", "user_id", "dep_st", "arr_st", "dep_time"]
        self.cur.execute(qer)
        values = self.cur.fetchall()
        return [{keys[i]: val[i] for i in range(5)} for val in values]

    def get_one_cache_path(self, uid: int, pid: int) -> dict[str,]:
        """
        Возвращает один конкретный сохранённый маршрут пользователя.
        :param uid: Уникальный id пользователя.
        :param pid: `id` пути, который надо вернуть.
        :return: Возвращает путь в формате (Станция отправления, станция прибытия, время старое отправления)
        """
        qer = "SELECT path_id, user_id, dep_st, arr_st, dep_time FROM path_cache WHERE user_id = %s and path_id = %s;"
        keys = ["path_id", "user_id", "dep_st", "arr_st", "dep_time"]
        params = [uid, pid]
        self.cur.execute(qer, params)
        val = self.cur.fetchall()[0]
        return {keys[i]: val[i] for i in range(5)}

    # <-------------------------------------------------PATH_CACHE------------------------------------------------->
    # <--------------------------------------------------GET_JSON-------------------------------------------------->

    def get_user_path(self, uid: int) -> list[dict[str,]]:
        keys = ["path_id", "user_id", "dep_st", "arr_st", "dep_time"]
        qer = (f"SELECT {', '.join(keys)} FROM path_cache "
               "WHERE user_id = %s;")

        params = [uid]
        self.cur.execute(qer, params)
        vals = self.cur.fetchall()
        return [{keys[i]: val[i] for i in range(len(keys))} for val in vals]

    def get_user_req(self, uid: int) -> list[dict[str,]]:
        keys = ["dep_st_id", "arr_st_id", "dep_time", "sort_type", "filter_type", "col", "is_mlt"]
        qer = (f"SELECT {', '.join(keys)} FROM req_cache "
               f"WHERE user_id = %s;")

        params = [uid]
        self.cur.execute(qer, params)
        vals = self.cur.fetchall()
        return [{keys[i]: val[i] for i in range(len(keys))} for val in vals]

    def get_user_settings(self, uid: int) -> dict[str,]:
        keys = ["id", "name", "filter_type", "sort_type", "col", "chat_id"]
        qer = (f"SELECT {', '.join(keys)} FROM users "
               f"WHERE id = %s LIMIT 1;")

        params = [uid]
        self.cur.execute(qer, params)
        val = self.cur.fetchall()[0]
        return {keys[i]: val[i] for i in range(len(keys))}


DB = DataBase()


def ind_format(identification: str) -> str | int:
    try:
        identification = int(identification)
    except:
        ...

    return identification
