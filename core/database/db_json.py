from database.dataframe import DataBase


class _DBJson(DataBase):
    def get_user_path(self, uid: int) -> list[dict[str, ]]:
        """
        Запрос на получение всех сохранённых маршрутов пользователя.
        :param uid: Уникальный id пользователя.
        :return: Список словарей с полями сохранёнными в БД маршрутов.
        """
        keys = ["path_id", "user_id", "dep_st", "arr_st", "dep_time"]
        qer = (f"SELECT {', '.join(keys)} FROM path_cache "
               "WHERE user_id = %s;")

        params = [uid]
        self.cur.execute(qer, params)
        vals = self.cur.fetchall()
        return [{keys[i]: val[i] for i in range(len(keys))} for val in vals]

    def get_user_req(self, uid: int) -> list[dict[str, ]]:
        """
        Запрос на получение всех сохранённых запросов пользователя.
        :param uid: Уникальный id пользователя.
        :return: Список словарей с полями сохранёнными в БД запросов.
        """
        keys = ["dep_st_id", "arr_st_id", "dep_time", "sort_type", "filter_type", "col", "is_mlt", "name"]
        qer = (f"SELECT {', '.join(keys)} FROM req_cache "
               f"WHERE user_id = %s;")

        params = [uid]
        self.cur.execute(qer, params)
        vals = self.cur.fetchall()
        return [{keys[i]: val[i] for i in range(len(keys))} for val in vals]

    def get_user_settings(self, uid: int) -> dict[str, ]:
        """
        Запрос на получение всех настроек пользователя.
        :param uid: Уникальный id пользователя.
        :return: Список словарей с полями сохранёнными в БД настроек.
        """
        keys = ["id", "name", "filter_type", "sort_type", "col", "chat_id"]
        qer = (f"SELECT {', '.join(keys)} FROM users "
               f"WHERE id = %s LIMIT 1;")

        params = [uid]
        self.cur.execute(qer, params)
        val = self.cur.fetchall()[0]
        return {keys[i]: val[i] for i in range(len(keys))}


DBJson = _DBJson()
