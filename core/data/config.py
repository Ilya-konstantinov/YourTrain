User_agent = ""

Headers = {
    "User-Agent": User_agent
}

TOKEN = ""

ADMIN_CHAT_ID = 0

DB_DATA = {
    "username": "",
    "passwd": "",
    "database": "",
    "host": "",
    "port": 0
}

sort_dict = {
    ('0', 'departure_time', 'dpt', "отправлении"): 0,
    ('1', 'arrival_time', 'art', "прибытии"): 1,
    ('2', 'path_time', 'pht', "время пути"): 2,
}

filter_dict = {
    ('0', 'all', "все"): 0,
    ("1", 'speed', 'sd', "скоростные"): 1,
    ('2', 'rg', "обычные"): 2,
}

type_interp = {
    ("sort", "sort_type", "сортировка"): "sort_type",
    ("filter", "filter_type", "фильтр"): "filter_type",
    ("name", "имя", "обращение"): "name",
    ("col", "количество"): "col",
    "dep_time": "dep_time"
}

sort_ind_to_rus = [
    "Отправлении",
    "Прибытии",
    "Время пути"
]

filter_ind_to_rus = [
    "Все",
    "Скоростные",
    "Обычные"
]

DB_DEFAULT = [0, 0, 5]
