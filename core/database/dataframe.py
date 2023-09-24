from mysql.connector import connect
from core.data.config import DB_DATA, DB_DEFAULT


class DataBase:
    def __init__(self):
        self.cnx = connect(**DB_DATA)
        self.cur = self.cnx.cursor()
        self.cnx.autocommit = True

    # def db_trans(func_to_decr):
    #     def trans(self, *args, **kwargs):
    #         self.cnx.start_transaction()
    #         ans = func_to_decr(self, *args, **kwargs)
    #         self.cnx.commit()
    #         return ans
    #
    #     return trans

    # @db_trans
    def user_create(self, uid: int, name: str) -> None:
        qer = "INSERT INTO users (id, name, filter_type, sort_type, col) VALUES (%s, %s, %s, %s, %s);"
        self.cur.execute(qer, (uid, name, *DB_DEFAULT))

    def user_exist(self, uid: int) -> bool:
        qer = "SELECT name FROM users WHERE id = %s"
        self.cur.execute(qer, [uid])
        return not (self.cur.fetchone() is None)

    def user_params(self, uid: int):
        qer = "SELECT name, filter_type, sort_type, col FROM users WHERE id = %s;"
        self.cur.execute(qer, tuple([uid]))
        return self.cur.fetchone()

    def set_params(self, uid: int, param_key: str, param_val: int):
        qer = f"UPDATE users SET {param_key} = %s WHERE id = %s;"
        params = (param_val, uid)
        self.cur.execute(qer, params)


DB = DataBase()
