from aiogram.filters.callback_data import CallbackData


class ReqCallbackFactory(CallbackData, prefix='re'):
    action: str
    params: str