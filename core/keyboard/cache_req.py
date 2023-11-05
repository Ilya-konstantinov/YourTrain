from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from callback.req import ReqCallbackFactory
from data.config import filter_ind_to_rus, sort_ind_to_rus
from model.path import CacheRequest


def cache_req_inline(reqs: list[CacheRequest]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for req in reqs:
        builder.button(
            text=req.name,
            callback_data=ReqCallbackFactory(
                action="req",
                params=req.get_params(),
            )
        )
    return builder.as_markup()


def cache_req_reply(reqs: list[CacheRequest]) -> ReplyKeyboardMarkup:
    is_empty = len(reqs)
    builder = ReplyKeyboardBuilder(
        markup=[
            [
                KeyboardButton(text="Изменить"),
                KeyboardButton(text="Удалить"),
            ] if is_empty else [],
            [
                KeyboardButton(text="Создать"),
                KeyboardButton(text="Отмена")
            ],
            []
        ],
    )

    for req in reqs:
        builder.button(
            text=req.name
        )

    kb = builder.as_markup()
    kb.resize_keyboard = True
    return kb


def schet(col: int) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for i in range(col):
        builder.button(text=str(i+1))
    kb = builder.as_markup()
    kb.resize_keyboard = True
    return kb


def change_cached(req: CacheRequest) -> ReplyKeyboardMarkup:
    dep_time = req.dep_time
    if dep_time in [0, '0', None, '-']:
        dep_time = "Сейчас"

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=f'Время отправления: {dep_time}'),
                KeyboardButton(text=f'Количество электричек: {req.col}'),
                KeyboardButton(text=f'Имя: {req.name}')
            ],
            [
                KeyboardButton(text=f'Тип сортировки: {sort_ind_to_rus[req.sort_type]}'),
                KeyboardButton(text=f'Тип фильтрации: {filter_ind_to_rus[req.filter_type]}')
            ],
            [
                KeyboardButton(text="Отмена"),
                KeyboardButton(text="Сохранить запрос")
            ]
        ],
        resize_keyboard=True
    )
    return kb
