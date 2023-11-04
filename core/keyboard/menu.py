from aiogram.utils.keyboard import (ReplyKeyboardMarkup, ReplyKeyboardBuilder)
from aiogram.types import KeyboardButton
from model.path import CacheRequest


def menu(*args) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder(
        [
            [
                KeyboardButton(text="Запрос"),
                KeyboardButton(text="Отзыв")
            ],
            [
                KeyboardButton(text="Сохранённые запросы")
            ]
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
