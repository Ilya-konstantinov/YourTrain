from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def comment_args() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Анонимно"),
                   KeyboardButton(text="Не анонимно")]],
        resize_keyboard=True,
        is_persistent=True
    )
    return kb
