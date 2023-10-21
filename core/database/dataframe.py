from typing import Tuple

from mysql.connector import connect
from core.data.config import DB_DATA, DB_DEFAULT
from datetime import datetime, timedelta
from core.model.path import Station, Path
import json


class DataBase:
    def __init__(self):
        self.cnx = connect(**DB_DATA)
        self.cur = self.cnx.cursor()
        self.cnx.autocommit = True

    def user_create(self, uid: int, name: str, chat_id: int) -> None:
        qer = "INSERT INTO users (id, name, chat_id, filter_type, sort_type, col) VALUES (%s, %s, %s, %s, %s, %s);"
        self.cur.execute(qer, (uid, name, chat_id, *DB_DEFAULT))

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

    def cache_req_col(self, uid: int) -> int:
        qer = 'SELECT number FROM req_cache WHERE user_id = %s ORDER BY number DESC LIMIT 1;'
        params = [uid]
        self.cur.execute(qer, params)
        ans = self.cur.fetchone()
        if ans is None:
            return 0

        return ans[0]

    def cache_req_exists(self, uid: int, identification: str | int) -> bool:
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

    def station_by_id(self, st_id: int) -> str:
        qer = "SELECT title FROM station_cache WHERE id = %s"
        params = [st_id]
        self.cur.execute(qer, params)
        return self.cur.fetchone()[0]

    def station_create(self, st: Station):
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

    def path_exists(self, uid: int, pid: int) -> bool:
        qer = "SELECT * FROM path_cache WHERE user_id = %s and path_id = %s"
        params = [uid, pid]
        self.cur.execute(qer, params)
        return not (self.cur.fetchone() is None)

    def cache_path_create(self, uid: int, path: Path):
        if self.path_exists(uid, path.path_id):
            return False

        qer = ("INSERT INTO path_cache(path_id, user_id, dep_st, arr_st, dep_time) "
               "VALUES (%s, %s, %s, %s, %s)")
        params = [path.path_id, uid, path.dep_st.id, path.arr_st.id, path.departure_time]
        self.cur.execute(qer, params)
        return True

    def cache_path_get(self, uid: int, path: int) -> tuple[Station, Station, datetime] | bool:
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

    def get_whole_cache_path(self) -> list[dict[str, ]]:
        qer = "SELECT path_id, user_id, dep_st, arr_st, dep_time FROM path_cache"
        keys = ["path_id", "user_id", "dep_st", "arr_st", "dep_time"]
        self.cur.execute(qer)
        values = self.cur.fetchall()
        return [{keys[i]: val[i] for i in range(5)} for val in values]

    def get_one_cache_path(self, uid: int, pid: int) -> dict[str, ]:
        qer = "SELECT path_id, user_id, dep_st, arr_st, dep_time FROM path_cache WHERE user_id = %s and path_id = %s"
        keys = ["path_id", "user_id", "dep_st", "arr_st", "dep_time"]
        params = [uid, pid]
        self.cur.execute(qer, params)
        val = self.cur.fetchone()
        return {keys[i]: val[i] for i in range(5)}


DB = DataBase()


def ind_format(identification: str) -> str | int:
    try:
        identification = int(identification)
    except:
        ...

    return identification
