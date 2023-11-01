from aiogram.fsm.state import State, StatesGroup


class CachePath(StatesGroup):
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
    get_sort = State()
    get_time = State()
    get_filter = State()
    get_col = State()
