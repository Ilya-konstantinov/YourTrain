from aiogram import Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import keyboard.menu
import model.model
from FSMachines import MStates
from callback.req import PathCallbackFactory
from database.db_cache_path import DBCachePath
from database.db_user import DBUser
from keyboard import req_args
from keyboard.cache_path import cache_menu
from logic.cache_path import cache_path, bl_path_view
from logic.service import bl_get_nearest_cache_req
from model.path import CacheRequest, CachePath


def hand(dp: Dispatcher):
    """
    Внесение функций в хендлер
    """
    @dp.message(Command("path_cache"))
    async def cmd_path_cache(message: Message, command: CommandObject, state: FSMContext):
        """
        Начало создания нового сохранённого маршрута. Вызов какого-либо запроса с данными аргументами.
        """
        await state.set_state(MStates.CachePath.get_path)
        ans = await cache_path(message.from_user.id, command.args)
        if isinstance(ans, str):
            await message.answer(ans, reply_markup=cache_menu())
            return

        await state.update_data(paths=ans[1])
        await message.answer(ans[0] + "\nВыведите номер пути, который хотите добавить\n⠀",
                             parse_mode=ParseMode.MARKDOWN_V2)

    @dp.message(MStates.CachePath.get_path)
    async def path_num(message: Message, state: FSMContext):
        """
        Выбор какого-то маршрута из представленных ранее или сообщение о неправильном номере.
        """
        await state.set_state(MStates.CachePath.just_menu)
        num = message.text
        paths = (await state.get_data())['paths']
        try:
            num = int(num)
            assert 1 <= num <= len(paths)
        except:
            await state.clear()
            await message.answer("Вы указали неправильный номер!", reply_markup=cache_menu())
            return
        path = paths[num - 1]
        path: CachePath = CachePath(
            dep_st=path.dep_st, arr_st=path.arr_st,
            dep_time=path.dep_time, path_id=path.path_id,
            user_id=message.from_user.id, only_updates=False
        )
        DBCachePath.cache_path_create(message.from_user.id, path)
        await message.answer("Ваш маршрут добавлен", reply_markup=cache_menu(), parse_mode=ParseMode.MARKDOWN_V2)
        ans = bl_path_view(message.from_user.id)
        await message.answer(ans)

    @dp.callback_query(PathCallbackFactory.filter())
    async def func(
            callback: CallbackQuery,
            callback_data: PathCallbackFactory,
    ):
        """
        Обработка удаления сохранённых запросов через Inline кнопки.
        """
        if callback_data.action == "del":
            args = (callback.from_user.id, callback_data.pid)
            DBCachePath.del_cache_path(*args)
            await callback.message.answer("Ваш путь успешно удалён")
        if callback_data.action == "print":
            ans = model.model.nocache_path_view(callback_data.pid)
            await callback.message.answer(f'```\n{ans}```', parse_mode=ParseMode.MARKDOWN_V2)
        await callback.answer()

    @dp.message(MStates.CachePath.just_menu, F.text.casefold() == "создать")
    async def create(message: Message, state: FSMContext):
        """
        Создание нового сохранённого маршрута через hd_req.py.
        """
        await state.clear()
        await state.set_state(MStates.Request.get_st_from)
        await state.update_data(req=CacheRequest(None, None, '-',
                                                 *DBUser.user_params(message.from_user.id)[1:],
                                                 is_mlt=False, user_id=message.from_user.id),
                                action='cache_path')
        await message.answer(
            text="Введите станцию(ии) отправления",
            reply_markup=req_args.stations()
        )

    @dp.message(MStates.CachePath.just_menu, F.text.casefold() == "отмена")
    async def _(message: Message, state: FSMContext) :
        """
        Возвращение к стандартному меню.
        """
        await state.clear()
        await state.set_state(MStates.Menu.just_menu)
        await message.answer("Возвращаю",
                             reply_markup=keyboard.menu.menu(*bl_get_nearest_cache_req(message.from_user.id)[1:]))

    @dp.message(MStates.Menu.just_menu, F.text.casefold() == "сохранённые маршруты")
    async def _(message: Message, state: FSMContext):
        """
        Открытие меню сохранённых маршрутов.
        """
        await state.clear()
        await state.set_state(MStates.CachePath.just_menu)
        ans = bl_path_view(message.from_user.id)
        if not ans:
            ans = "У тебя еще нет сохранённых маршрутов"
        await message.answer(ans,
                             reply_markup=cache_menu(),
                             parse_mode=ParseMode.MARKDOWN_V2)
