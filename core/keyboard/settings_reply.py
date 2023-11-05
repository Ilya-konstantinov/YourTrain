from aiogram.types import KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardMarkup

from data.config import sort_ind_to_rus, filter_ind_to_rus


def give(sort_type: str | int, filter_type: str | int, col: int) -> ReplyKeyboardMarkup:
    """
    Генерирует клавиатуру настроек. Подставляет сортировку, фильтр и количество в текст кнопок.
    :param sort_type: Тип сортировки -- индекс или сама строка.
    :param filter_type: Тип фильтрации -- индекс или сама строка.
    :param col: Количество электричек в одном запросе.
    :return: Возвращает клавиатуру настроек.
    """

    if isinstance(sort_type, int):
        sort_type = sort_ind_to_rus[sort_type]

    if isinstance(filter_type, int):
        filter_type = filter_ind_to_rus[filter_type]

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Сбросить"),
                KeyboardButton(text="Скачать"),
                KeyboardButton(text="Очистить полностью")
            ],
            [
                KeyboardButton(text=f"Тип сортировки:\n{sort_type}"),
                KeyboardButton(text=f"Тип фильтрации:\n{filter_type}"),
                KeyboardButton(text=f"Количество электричек\nв одном запросе: {col}")
            ],
            [
                KeyboardButton(text="Имя"),
                KeyboardButton(text="Обратно"),
                KeyboardButton(text="Отзыв")
            ]
        ],
        resize_keyboard=True
    )
    return kb


def def_val(val_type: str):
    """
    Генерирует клавиатуру подсказок для изменения параметров стандратного запроса.
    :param val_type: Тип параметра, который будут изменять (sort, filter, col, name)
    :return: Возвращает клавиатуру с подсказками или `ReplyKeyboardRemove()` в случае `name`
    """

    ft, sc, th = [""] * 3
    match val_type:
        case "sort_type":
            ft, sc, th = sort_ind_to_rus
        case "filter_type":
            ft, sc, th = filter_ind_to_rus
        case "col":
            ft, sc, th = [str(i) for i in range(3, 8, 2)]
        case "name":
            return ReplyKeyboardRemove()
        case "dep_time":
            ft, sc, th = "4:20", "-", "+20"

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=ft),
                KeyboardButton(text=sc),
                KeyboardButton(text=th)
            ],
            [
                KeyboardButton(text="Обратно")
            ]
        ],
        resize_keyboard=True
    )
    return kb
