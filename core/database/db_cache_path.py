from datetime import datetime

from database.dataframe import DataBase
from database.db_station import DBStation
from model.path import CachePath


class _DBCachePath(DataBase):
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

    def cache_path_create(self, uid: int, path: CachePath):
        """
        Сохраняет маршрут пользователю.

        :param uid: Уникальный id пользователя.
        :param path: Путь, который необходимо добавить.
        :return: Возвращает False, если станцию создать не удалось.
        """
        if not DBStation.station_exists(path.dep_st):
            DBStation.station_create(path.dep_st)
        if not DBStation.station_exists(path.arr_st):
            DBStation.station_create(path.arr_st)

        if self.path_exists(uid, path.path_id):
            return False
        try:
            qer = ("INSERT INTO path_cache(path_id, user_id, dep_st, arr_st, dep_time, only_updates) "
                   "VALUES (%s, %s, %s, %s, %s, FALSE)")
            params = [path.path_id, uid, path.dep_st.id, path.arr_st.id, path.dep_time]
            self.cur.execute(qer, params)
        except Exception as e:
            return False
        return True

    def cache_path_get(self, uid: int, pid: int) -> CachePath | bool:
        """
        Возвращает параметры для запроса к API сохранённого маршрута.

        :param uid: Уникальный id пользователя.
        :param pid: `id` пути, который надо вернуть.
        :return: Возвращает параметры для запроса в формате
        (Станция отправления, станция прибытия, время старое отправления)
        """
        if not self.path_exists(uid, pid):
            return False

        keys = ["dep_st", "arr_st", "dep_time", "only_updates"]
        qer = f"SELECT {', '.join(keys)} FROM path_cache WHERE user_id = %s AND path_id = %s"
        params = [uid, pid]
        self.cur.execute(qer, params)
        dep_st, arr_st, dep_time, only_updates = self.cur.fetchone()

        dep_st, arr_st = DBStation.station_by_id(dep_st), DBStation.station_by_id(arr_st)
        dep_time = datetime.today().replace(hour=dep_time.seconds // 3600, minute=(dep_time.seconds % 3600) // 60)

        return CachePath(dep_st, arr_st, dep_time, only_updates, pid, uid)

    def get_whole_cache_path(self) -> list[CachePath]:
        """
        Возвращает все сохранённые маршруты.

        :return: Список в формате (Станция отправления, станция прибытия, время старое отправления).
        """

        keys = ["dep_st", "arr_st", "dep_time", "path_id", "user_id", "only_updates"]
        qer = f"SELECT {', '.join(keys)} FROM path_cache;"
        self.cur.execute(qer)
        values = list(self.cur.fetchall())
        for ind, val in enumerate(values):
            val = list(val)
            val[0] = DBStation.station_by_id(val[0])
            val[1] = DBStation.station_by_id(val[1])
            values[ind] = val
        return [CachePath(*val) for val in values]

    def get_one_cache_path(self, uid: int, pid: int) -> CachePath | bool:
        """
        Возвращает один конкретный сохранённый маршрут пользователя.

        :param uid: Уникальный id пользователя.
        :param pid: `id` пути, который надо вернуть.
        :return: Возвращает путь в формате (Станция отправления, станция прибытия, время старое отправления)
        """
        if not self.path_exists(uid=uid, pid=pid):
            return False

        keys = ["dep_st", "arr_st", "dep_time", "path_id", "user_id", "only_updates"]
        qer = f"SELECT {', '.join(keys)} FROM path_cache WHERE user_id = %s and path_id = %s LIMIT 1;"
        params = [uid, pid]
        self.cur.execute(qer, params)
        val = self.cur.fetchone()
        return CachePath(*val)

    def get_users_cache_path(self, uid: int) -> list[CachePath]:
        """
        Возвращает все сохранённые маршруты данного пользователя.

        :param uid: Уникальный id пользователя.
        :return: Возвращает список путей в формате [(Станция отправления, станция прибытия, время старое отправления)]
        """

        keys = [ "dep_st", "arr_st","dep_time", "path_id", "user_id", "only_updates"]
        qer = f"SELECT {', '.join(keys)} FROM path_cache WHERE user_id = %s;"
        params = [uid]
        self.cur.execute(qer, params)
        values = self.cur.fetchall()
        for ind, val in enumerate(values):
            val = list(val)
            val[0] = DBStation.station_by_id(val[0])
            val[1] = DBStation.station_by_id(val[1])
            values[ind] = val
        return [CachePath(*val) for val in values]

    def del_cache_path(self, uid: int, pid: int):
        """
        Удаляет путь pid у пользователя с id: uid
        :param uid: Уникальный id пользователя
        :param pid: Уникальный id пути
        """
        qer = "DELETE FROM path_cache WHERE user_id = %s and path_id = %s"
        param = [uid, pid]
        self.cur.execute(qer, param)


DBCachePath = _DBCachePath()
