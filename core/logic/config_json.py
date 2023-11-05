import json

from database.db_json import DBJson


async def get_json(uid: int) -> json:
    """
    Преобразование данных пользователя с данным uid в JSON.
    :param uid: Уникальный id пользователя.
    :return: Возвращает объект типа json, где хранятся все данные пользователя, которые есть в БД.
    """
    path = {'path_cache': DBJson.get_user_path(uid)}
    req = {'req_cache': DBJson.get_user_req(uid)}
    settings = {'setting': DBJson.get_user_settings(uid)}
    ans_json: json = json.dumps(path | req | settings, default=str)
    return ans_json
