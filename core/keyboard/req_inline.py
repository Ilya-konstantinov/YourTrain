from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callback.req import ReqCallbackFactory, PathCallbackFactory


def req_inline(args: str, pids: list[int]) -> InlineKeyboardMarkup:
    """
    Генерирует inline клавиатуру для ответа на запрос электричек.
    :param pids: `id` путей которые можно вывести.
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
    builder.adjust(3, len(pids))
    builder.attach(InlineKeyboardBuilder.from_markup(schet(pids)))
    kb = builder.as_markup()
    return kb


def schet(pids: list[int]) -> InlineKeyboardMarkup:
    """
    Генерация клавиатуры с путями для вывода.
    :param pids: `id` путей которые можно вывести.
    :return: Inline клавиатура.
    """
    builder = InlineKeyboardBuilder()
    for ind, pid in enumerate(pids):
        builder.button(text=str(ind + 1), callback_data=PathCallbackFactory(pid=pid, action="print"))
    kb = builder.as_markup()
    return kb
