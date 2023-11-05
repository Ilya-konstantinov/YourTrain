import json

from data.config import DB_DEFAULT
from database.dataframe import DataBase
from database.db_station import DBStation
from database.db_user import DBUser
from model.path import CacheRequest, CachePath


class _DBRecache(DataBase):

    def recache_req(self, req: CacheRequest) -> bool:
        """
        Изменяет электричку с данными параметрами в БД.

        :returns: Возвращает True если за спрос сохранён и False если сохранить запрос не получилось
        """
        keys = ["dep_st_id", "arr_st_id", "dep_time", "sort_type", "filter_type", "col", "is_mlt"]
        qer = f"UPDATE req_cache SET {[key + ' = %s' for key in keys]} WHERE user_id = %s and name = %s;"

        dep_st_id = json.dumps([st.id for st in req.dep_st])
        arr_st_id = json.dumps([st.id for st in req.arr_st])

        param = [dep_st_id, arr_st_id,
                 req.dep_time, req.sort_type, req.filter_type, req.col, req.is_mlt,
                 req.user_id, req.name]

        try:
            self.cur.execute(qer, param)
            return True
        except:
            return False

    def recache_path(self, path_old: CachePath, path_new: CachePath) -> bool:
        """
        Изменяет сохранённый путь с заданными значениями.

        :return: Возвращает True если запрос сохранён и False если сохранить запрос не получилось.
        """
        if not DBStation.station_exists(path_new.dep_st):
            DBStation.station_create(path_new.dep_st)
        if not DBStation.station_exists(path_new.arr_st):
            DBStation.station_create(path_new.arr_st)
        if not DBStation.station_exists(path_old.dep_st):
            DBStation.station_create(path_old.dep_st)
        if not DBStation.station_exists(path_old.arr_st):
            DBStation.station_create(path_old.arr_st)
        keys = ["path_id", "dep_st", "arr_st", "dep_time", "only_updates"]
        qer = f"UPDATE path_cache SET {', '.join([key + ' = %s' for key in keys])} WHERE user_id = %s and path_id = %s;"
        param = [path_new.path_id, path_new.dep_st.id, path_new.arr_st.id, path_new.dep_time,
                 path_new.only_updates, path_old.user_id, path_old.path_id]
        try:
            self.cur.execute(qer, param)
            return True
        except Exception as e:
            return False

    def recache_user(self, uid: int, name: str) -> bool:
        """
        Изменяет настройки пользователя на стандартные или создаёт нового пользователя со стандартными настройками.

        :param uid: Уникальный id пользователя.
        :param name: Имя пользователя.
        :return: Возвращает True в случае успеха, False иначе.
        """

        if not DBUser.user_exist(uid):
            return DBUser.user_create(uid, name)

        qer = "UPDATE users SET name = %s, sort_type = %s, filter_type = %s, col = %s, chat_id = %s WHERE id = %s;"
        param = [name, *DB_DEFAULT, uid, uid]
        try:
            self.cur.execute(qer, param)
        except:
            return False

        return True


DBRecache = _DBRecache()
