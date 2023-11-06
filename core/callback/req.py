from aiogram.filters.callback_data import CallbackData


class ReqCallbackFactory(CallbackData, prefix='re'):
    """
    Фабрика callback для запросов
    """
    action: str
    params: str


class PathCallbackFactory(CallbackData, prefix="pa"):
    """
    Фабрика callback для сохранённых маршрутов
    """
    action: str
    pid: int
