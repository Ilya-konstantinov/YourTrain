from database.dataframe import DataBase
from database.db_recache import DBRecache


class _DBDel(DataBase):
    
    def del_info(self, uid: int, name: str) -> bool:
        """
        Удаляет всю возможную информацию о пользователе.
        Создаёт нового пользователя с базовыми настройками.

        :param name: Имя пользователя.
        :param uid: Уникальный `id` пользователя.
        :return: Возвращает True если всё успешно, False иначе.
        """
        tables = ["path_cache", "req_cache", "users"]
        param = [uid]
        try:
            for table_name in tables:
                qer = f"DELETE FROM {table_name} WHERE {'user_id' if table_name != 'users' else 'id'} = %s;"
                self.cur.execute(qer, param)
        except:
            return False

        return DBRecache.recache_user(uid, name)


DBDel = _DBDel()
