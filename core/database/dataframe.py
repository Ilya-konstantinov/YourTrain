from typing import Tuple

from mysql.connector import connect
from core.data.config import DB_DATA, DB_DEFAULT
from datetime import datetime, timedelta
from core.model.path import Station
import json


class DataBase:
    def __init__(self):
        self.cnx = connect(**DB_DATA)
        self.cur = self.cnx.cursor()
        self.cnx.autocommit = True

    def user_create(self, uid: int, name: str) -> None:
        qer = "INSERT INTO users (id, name, filter_type, sort_type, col) VALUES (%s, %s, %s, %s, %s);"
        self.cur.execute(qer, (uid, name, *DB_DEFAULT))

    def user_exist(self, uid: int) -> bool:
        qer = "SELECT name FROM users WHERE id = %s"
        self.cur.execute(qer, [uid])
        return not (self.cur.fetchone() is None)

    def user_params(self, uid: int):
        qer = "SELECT name, sort_type, filter_type, col FROM users WHERE id = %s;"
        self.cur.execute(qer, tuple([uid]))
        return self.cur.fetchone()

    def set_params(self, uid: int, param_key: str, param_val: int):
        qer = f"UPDATE users SET {param_key} = %s WHERE id = %s;"
        params = (param_val, uid)
        self.cur.execute(qer, params)

    def cache_req_col(self, uid: int) -> int:  # TODO need test
        qer = 'SELECT number FROM req_cache WHERE user_id = %s ORDER BY number DESC LIMIT 1;'
        params = [uid]
        self.cur.execute(qer, params)
        ans = self.cur.fetchone()
        if ans is None:
            return 0

        return ans[0]

    def cache_req_exists(self, uid: int, identification: str | int) -> bool:  # TODO need test
        column_title = ('name' if isinstance(identification, str) else 'number')
        qer = f"SELECT * FROM req_cache WHERE {column_title} = %s AND user_id = %s;"
        params = [identification, uid]
        self.cur.execute(qer, params)
        return not (self.cur.fetchone() is None)

    def cache_req_create(self, uid: int, name: str, dep_st_id: list[int], arr_st_id: list[int], sort_type: int,
                         filter_type: int, col: int, is_mlt: bool, dep_time: datetime) -> bool:
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

    def cache_req_get(self, uid: int, identification: str | int) -> bool | tuple[str, str, bool]:  # TODO need test
        if not self.cache_req_exists(uid, identification):
            return False

        column_title = ('name' if isinstance(identification, str) else 'number')
        qer = (f"SELECT dep_st_id, arr_st_id, dep_type, sort_type, filter_type, col, is_mlt FROM req_cache "
               f"WHERE {column_title} = %s AND user_id = %s;")
        params = [identification, uid]
        self.cur.execute(qer, params)
        ans = list(self.cur.fetchone())
        dep_time, sort_type, filter_type, col = ans[2:-1]

        if dep_time is None:
            dep_time = datetime.now()

        is_mlt: bool = bool(ans[-1])
        dep_st_id, arr_st_id = ans[:2]
        dep_st_id, arr_st_id = json.load(dep_st_id), json.load(arr_st_id)

        for ind, st in enumerate(dep_st_id):
            dep_st_id[ind] = self.station_by_id(st)

        for ind, st in enumerate(arr_st_id):
            arr_st_id[ind] = self.station_by_id(st)

        stations: str = (' -- ' if is_mlt else ' - ').join([' '.join(dep_st_id), ' '.join(arr_st_id)])
        args: str = ' '.join([str(arg) for arg in [dep_time, sort_type, filter_type, col]])
        return stations, args, is_mlt

    def station_by_id(self, st_id: int) -> int:  # TODO need test
        qer = "SELECT title FROM station_cache WHERE id = %s"
        params = [st_id]
        self.cur.execute(qer, params)
        return self.cur.fetchone()[0]

    def station_create(self, st: Station):  # TODO need test
        qer = "INSERT INTO station_cache (id, title) VALUES (%s, %s);"
        params = [st.id, st.title]
        try:
            self.cur.execute(qer, params)
        except:
            return False

    def station_exists(self, st: Station):
        qer = "SELECT * FROM station_cache WHERE id = %s"
        params = [st.id]
        self.cur.execute(qer, params)
        return not (self.cur.fetchone() is None)

DB = DataBase()
