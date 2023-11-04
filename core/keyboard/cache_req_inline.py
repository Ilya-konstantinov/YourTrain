from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callback.req import ReqCallbackFactory
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
