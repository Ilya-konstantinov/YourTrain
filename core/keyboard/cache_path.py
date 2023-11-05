from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callback.req import PathCallbackFactory


def path_inline(pid: int, uid: int) -> InlineKeyboardMarkup:
    """
    Генерация Inline кнопки "удалить" для сохранённого маршрута.
    :param pid: `id` маршрута.
    :param uid: Уникальный id пользователя
    :return: Inline кнопка удаления сохранённого маршрута
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="Удалить", callback_data=PathCallbackFactory(pid=pid, uid=uid))

    return kb.as_markup()


def cache_menu() -> ReplyKeyboardMarkup:
    """
    Генерация меню для сохранённых маршрутов.
    :return:
    """
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать"),
             KeyboardButton(text="Удалить")],
            [KeyboardButton(text="Обратно")]
        ]
    )
    return kb
