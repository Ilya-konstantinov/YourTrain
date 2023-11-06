# Числовые интерпретации определений фильтрации
sort_dict = {
    ('0', 'departure_time', 'dpt', "отправлении"): 0,
    ('1', 'arrival_time', 'art', "прибытии"): 1,
    ('2', 'path_time', 'pht', "в_пути"): 2,
}
# Числовые интерпретации определений фильтрации
filter_dict = {
    ('0', 'all', "все"): 0,
    ("1", 'speed', 'sd', "скоростные"): 1,
    ('2', 'rg', "обычные"): 2,
}
# Интерпретации принятые для определений в коде
type_interp = {
    ("sort", "sort_type", "сортировка"): "sort_type",
    ("filter", "filter_type", "фильтр"): "filter_type",
    ("name", "имя", "обращение"): "name",
    ("col", "количество"): "col",
    "dep_time": "dep_time"
}
# Русская интерпретация определения сортировки
sort_ind_to_rus = [
    "Отправлении",
    "Прибытии",
    "В_пути"
]
# Русская интерпретация определения фильтра
filter_ind_to_rus = [
    "Все",
    "Скоростные",
    "Обычные"
]
# Значения параметров запросов всех пользователей по умолчанию
DB_DEFAULT = [0, 0, 5]
