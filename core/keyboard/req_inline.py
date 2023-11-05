from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callback.req import ReqCallbackFactory


def req_inline(args) -> InlineKeyboardMarkup:
    """
    Генерирует inline клавиатуру для ответа на запрос электричек.
    :param args: Аргументы запроса.
    :return: Inline клавиатура с возможностями "повторить запрос", "сохранить маршрут" и "сохранить запрос".
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Повторить запрос",
        callback_data=ReqCallbackFactory(action="req", params=args)
    )
    builder.button(
        text="Сохранить маршрут",
        callback_data=ReqCallbackFactory(action="cache_path", params=args)
    )
    builder.button(
        text="Сохранить запрос",
        callback_data=ReqCallbackFactory(action="cache_req", params=args)
    )
    return builder.as_markup()
