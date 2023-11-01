from aiogram.utils.keyboard import (ReplyKeyboardMarkup,
                                    InlineKeyboardMarkup, InlineKeyboardBuilder, InlineKeyboardButton)
from aiogram.types import KeyboardButton
from model.path import CacheRequest
from callback.req import ReqCallbackFactory


def menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Запрос"),
                KeyboardButton(text="Отзыв")
            ],
            [
                KeyboardButton(text="Сохранённые запросы")
            ]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    return builder

