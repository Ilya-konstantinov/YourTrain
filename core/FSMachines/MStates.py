from aiogram.fsm.state import State, StatesGroup


class CachePath(StatesGroup):
    """
    Машина состояний сохранённых маршрутов
    """
    just_menu = State()
    get_path = State()
    num_path = State()


class Comment(StatesGroup):
    """
    Машина состояний отзыва
    """
    get_args = State()
    set_comment = State()


class Menu(StatesGroup):
    """
    Машина состояний меню
    """
    just_menu = State()


class Request(StatesGroup):
    """
    Машина состояний запроса
    """
    get_st_from = State()
    get_st_to = State()
    get_args = State()

    # Arguments
    change_args = State()


class CacheRequest(StatesGroup):
    """
    Машина состояний сохранённых запросов (inline)
    """
    get_name = State()


class Settings(StatesGroup):
    """
    Машина состояний настроек
    """
    just_menu = State()
    change_def = State()


class CacheReq(StatesGroup):
    """
    Машина состояний сохранённых запросов
    """
    change_args = State()
    just_menu = State()
    change = State()
    change_cached = State()
    get_name = State()
