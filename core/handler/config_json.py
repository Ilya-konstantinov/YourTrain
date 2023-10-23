from database.dataframe import DB
import json


async def get_json(uid: int):
    tmp_json = []
    path = {'path_cache': DB.get_user_path(uid)}
    req = {'req_cache': DB.get_user_req(uid)}
    settings = {'setting': DB.get_user_settings(uid)}
    ans_json = json.dumps(path | req | settings, default=str)
    return ans_json