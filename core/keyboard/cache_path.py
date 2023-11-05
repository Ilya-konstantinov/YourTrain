from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callback.req import PathCallbackFactory


def path_inline(pid: int, uid: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Удалить", callback_data=PathCallbackFactory(pid=pid, uid=uid))

    return kb.as_markup()


def cache_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать"),
             KeyboardButton(text="Удалить")],
            [KeyboardButton(text="Обратно")]
        ]
    )
    return kb
