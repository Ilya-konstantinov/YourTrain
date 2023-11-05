from aiogram.utils.keyboard import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton
from data.config import sort_ind_to_rus, filter_ind_to_rus
from model.path import CacheRequest


def stations() -> ReplyKeyboardMarkup:
    kk = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True
    )

    return kk


def args(req: CacheRequest) -> ReplyKeyboardMarkup:
    dep_time, sort_type, filter_type = req.dep_time, req.sort_type, req.filter_type
    if req.dep_time in [0, '0', None, '-']:
        dep_time = "Сейчас"

    if isinstance(req.sort_type, int):
        sort_type = sort_ind_to_rus[req.sort_type]

    if isinstance(req.filter_type, int):
        filter_type = filter_ind_to_rus[req.filter_type]

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=f'Время отправления: {dep_time}'),
                KeyboardButton(text=f'Количество электричек: {req.col}')
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
