from database.dataframe import DataBase
from model.path import Station


class _DBStation(DataBase):
    def station_exists(self, st: Station | int) -> bool:
        """
        Проверяет, существует ли станция.

        :param st: Станция, которая идет на проверку.
        :return: True если станция существует, False в ином случае.
        """
        if isinstance(st, Station):
            st = st.id

        qer = "SELECT * FROM station_cache WHERE id = %s"
        params = [st]
        self.cur.execute(qer, params)
        return not (self.cur.fetchone() is None)

    def station_by_id(self, st_id: int) -> Station | bool:
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
        return Station(
            id=st_id,
            title=self.cur.fetchone()[0]
        )

    def station_create(self, st: Station) -> None:
        """
        Создает станцию.

        :param st: Станция, которую надо создать.
        :return: Создает станцию. Если такая станция существует, то ничего не делает
        """
        qer = "INSERT INTO station_cache (id, title) VALUES (%s, %s);"
        params = [st.id, st.title]
        try:
            self.cur.execute(qer, params)
            if self.cnx.in_transaction:
                self.cnx.commit()
                self.cnx.start_transaction()
        except Exception as e:
            return


DBStation = _DBStation()
