from data.config import DB_DEFAULT
from database.dataframe import DataBase


class _DBUser(DataBase):
    def user_exist(self, uid: int) -> bool:
        """
        Проверка существует ли пользователь с заданным id.

        :param uid: Уникальный id пользователя.
        :returns: Возвращает True если пользователь существует, иначе False.
        """
        qer = "SELECT name FROM users WHERE id = %s LIMIT 1"
        self.cur.execute(qer, [uid])
        return not (self.cur.fetchone() is None)

    def user_params(self, uid: int) -> tuple[str | int] | bool:
        """
        Возвращает параметры по умолчанию для user.

        :param uid: Уникальный id пользователя.
        :returns: Возвращает (name, sort_type, filter_type, col) если пользователь есть, иначе False.
        """
        if not self.user_exist(uid):
            return False

        qer = "SELECT name, sort_type, filter_type, col FROM users WHERE id = %s;"
        self.cur.execute(qer, tuple([uid]))
        return self.cur.fetchone()

    def user_create(
            self, uid: int,
            name: str,
            chat_id: int = -1
    ) -> bool:
        """
        Создание user.

        :param uid: `id` пользователя.
        :param name: Обращение к пользователю.
        :param chat_id: `id` часа с пользователем.
        :returns: Возвращает True, если удается создать нового юзера, False если не получается.
        """
        if self.user_exist(uid):
            return False

        if chat_id == -1:
            chat_id = uid

        qer = "INSERT INTO users (id, name, chat_id, filter_type, sort_type, col) VALUES (%s, %s, %s, %s, %s, %s);"
        self.cur.execute(qer, (uid, name, chat_id, *DB_DEFAULT))
        return True

    def set_params(self, uid: int, param_key: str, param_val: int) -> bool:
        """
        Изменяет параметр по умолчанию для user

        :param uid: Уникальный id пользователя.
        :param param_key: Имя параметра, который необходимо изменить.
        :param param_val: Значение, на которое изменяется параметр.
        :returns: True если успешное изменение, False если нет такого user.
        """
        if not self.user_exist(uid):
            return False
        qer = f"UPDATE users SET {param_key} = %s WHERE id = %s;"
        params = (param_val, uid)
        self.cur.execute(qer, params)
        return True


DBUser = _DBUser()
