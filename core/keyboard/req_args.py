from aiogram.utils.keyboard import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton


def stations() -> ReplyKeyboardMarkup:
    kk = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True
    )

    return kk


def args(dep_time, sort_type, filter_type, col) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=f'Время отправления: {dep_time}'),
                KeyboardButton(text=f'Количество электричек: {col}')
            ],
            [
                KeyboardButton(text=f'Тип сортировки: {sort_type}'),
                KeyboardButton(text=f'Тип фильтрации: {filter_type}')
            ],
            [
                KeyboardButton(text="Отмена"),
                KeyboardButton(text="Сделать запрос")
            ]
        ],
        resize_keyboard=True
    )
    return kb
