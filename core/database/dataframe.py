from mysql.connector import connect

from data.config import DB_DATA


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
        self.cur.reset()

    def __del__(self):
        self.cur.close()
        self.cnx.close()
