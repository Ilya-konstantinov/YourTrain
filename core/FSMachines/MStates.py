from aiogram.fsm.state import State, StatesGroup


class CachePath(StatesGroup):
    just_menu = State()
    get_path = State()
    num_path = State()


class Comment(StatesGroup):
    get_args = State()
    set_comment = State()


class Menu(StatesGroup):
    just_menu = State()


class Request(StatesGroup):
    get_st_from = State()
    get_st_to = State()
    get_args = State()

    # Arguments
    change_args = State()


class CacheRequest(StatesGroup):
    get_name = State()


class Settings(StatesGroup):
    just_settings = State()
    change_def = State()


class CacheReq(StatesGroup):
    change_args = State()
    just_cache = State()
    change = State()
    change_cached = State()
    get_name = State()
