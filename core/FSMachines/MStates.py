from aiogram.fsm.state import State, StatesGroup


class CachePath(StatesGroup):
    get_path = State()
    num_path = State()
