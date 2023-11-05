from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import (ReplyKeyboardMarkup, ReplyKeyboardBuilder)

from model.path import CacheRequest


def menu(*args) -> ReplyKeyboardMarkup:
    """
    Генерация стандартного меню с сохранёнными запросами.
    :param args: Сохранённые запросы, которые будут видны нижней сточкой клавиатуры.
    :return: Reply клавиатура стандартного меню.
    """
    builder = ReplyKeyboardBuilder(
        [
            [
                KeyboardButton(text="Запрос"),
                KeyboardButton(text="Настройки")
            ],
            [
                KeyboardButton(text="Сохранённые запросы"),
                KeyboardButton(text="Сохранённые маршруты")
            ], []
        ],
    )

    for el in args:
        if isinstance(el, str):
            builder.button(
                text=el
            )
        if isinstance(el, CacheRequest):
            builder.button(
                text=el.name
            )

    kb = builder.as_markup()
    kb.resize_keyboard = True
    kb.is_persistent = True

    return kb
