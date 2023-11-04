import json

from database.dataframe import DataBase
from database.db_station import DBStation
from model.path import CacheRequest, Station


class _DBCacheReq(DataBase):
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

        return 0 if ans is None else ans[0]

    
    def cache_req_create(self, req: CacheRequest) -> bool:
        """
        Сохраняет электричку с данными параметрами в БД.

        :returns: Возвращает True если за спрос сохранён и False если сохранить запрос не получилось
        """
        if self.cache_req_exists(req.user_id, req.name):
            return False
        req_col: int = self.cache_req_col(req.user_id) + 1
        qer: str = ("INSERT INTO req_cache (dep_st_id, arr_st_id, sort_type, filter_type, "
                    "dep_time, is_mlt, user_id, name, number, col) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);")

        for st in req.dep_st:
            if not DBStation.station_exists(st):
                DBStation.station_create(st)

        for st in req.arr_st:
            if not DBStation.station_exists(st):
                DBStation.station_create(st)

        dep_st_id: str = json.dumps([st.id for st in req.dep_st])
        arr_st_id: str = json.dumps([st.id for st in req.arr_st])
        params = (dep_st_id, arr_st_id, req.sort_type, req.filter_type, req.dep_time, req.is_mlt,
                  req.user_id, req.name, req_col, req.col)
        try:
            self.cur.execute(qer, params)
            return True
        except Exception as e:
            return False

    def cache_req_get(self, uid: int, identification: str | int) -> bool | CacheRequest:
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

        keys = ["dep_st_id", "arr_st_id", "dep_time", "sort_type", "filter_type", "col", "is_mlt", "user_id", "name"]
        qer = (f"SELECT {', '.join(keys)} FROM req_cache "
               f"WHERE {column_title} = %s AND user_id = %s;")
        params = [identification, uid]
        self.cur.execute(qer, params)
        ans = list(self.cur.fetchone())

        ans[0], ans[1] = json.loads(ans[0]), json.loads(ans[1])


        for ind, st in enumerate(ans[0]):
            ans[0][ind] = DBStation.station_by_id(st)

        for ind, st in enumerate(ans[1]):
            ans[1][ind] = DBStation.station_by_id(st)

        req = CacheRequest(*ans)

        return req

    def cache_req_whole_get(self, uid: int) -> list[CacheRequest]:
        keys = ["dep_st_id", "arr_st_id", "dep_time", "sort_type", "filter_type", "col", "is_mlt", "user_id", "name"]
        qer = f"SELECT {', '.join(keys)} FROM req_cache WHERE user_id = %s;"
        params = [uid]
        self.cur.execute(qer, params)

        ans: list[tuple] = self.cur.fetchall()
        ans: list[CacheRequest | list] = [list(row) for row in ans]

        for ind_r, req in enumerate(ans):
            req[0], req[1] = json.loads(req[0]), json.loads(req[1])

            for ind, st in enumerate(req[0]):
                req[0][ind] = Station(
                    id=st,
                    title=DBStation.station_by_id(st).title,
                )

            for ind, st in enumerate(req[1]):
                req[1][ind] = Station(
                    id=st,
                    title=DBStation.station_by_id(st).title
                )

            ans[ind_r] = CacheRequest(*req)

        return ans

    def get_nearest(self, uid: int) -> list[CacheRequest | None]:
        qer = "SELECT id FROM req_cache WHERE user_id = %s LIMIT 3;"
        ans = [None]*3
        params = [uid]
        self.cur.execute(qer, params)
        reqs = self.cur.fetchall()
        for ind, req in enumerate(reqs):
            ans[ind] = self.cache_req_get(uid, req[0])

        return ans


def ind_format(identification: str) -> str | int:
    try:
        identification = int(identification)
    except:
        ...

    return identification


DBCacheReq = _DBCacheReq()

