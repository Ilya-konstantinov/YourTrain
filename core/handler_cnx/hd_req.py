from aiogram import Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import logic.req
import model.model
from FSMachines import MStates
from callback.req import ReqCallbackFactory
from database.db_cache_req import DBCacheReq
from database.db_station import DBStation
from database.db_user import DBUser
from keyboard import req_inline, req_args, menu, settings_reply
from logic.cache_path import cache_path
from logic.req import bl_req, bl_mlt_req, check_station, bl_parse_change
from logic.service import bl_get_nearest_cache_req
from model.path import CacheRequest, Station


def hand(dp: Dispatcher):
    """
    Внесение функций в хендлер
    """
    @dp.message(Command("req"))
    async def cmd_req(message: Message, command: CommandObject):
        """
        Базовый вызов запроса расписания с аргументами.
        """
        ans = await bl_req(user_id=message.from_user.id, args=command.args)
        if ans[0] != '`':
            await message.answer(ans)
            return

        args = command.args.replace(":", '..')

        await message.answer(
            text=ans + '\n⠀',
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=req_inline.req_inline(args, [])
        )

    @dp.message(Command("multi_req", "mltreq"))
    async def mlt_req(message: Message, command: CommandObject):
        """
        Мультистанцевый вызов запроса расписания с аргументами.
        """
        ans = await bl_mlt_req(user_id=message.from_user.id, args=command.args)
        await message.answer(ans, parse_mode=ParseMode.MARKDOWN_V2)

    @dp.callback_query(ReqCallbackFactory.filter())
    async def callbacks_num_change_fab(
            callback: CallbackQuery,
            callback_data: ReqCallbackFactory,
            state: FSMContext
    ):
        """
        Обработка callback'ов запросов, а конкретнее:

        - Сохранение пути

        - Повторение запроса

        - Сохранение маршрута
        """
        args = callback_data.params
        match callback_data.action:
            case "req":
                await callback.message.answer(
                    text=await bl_req(callback.from_user.id, callback_data.params),
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=req_inline.req_inline(args, [])
                )
            case "cache_path":
                await state.clear()
                await state.set_state(MStates.CachePath.get_path)
                paths = (await cache_path(callback.from_user.id,args))[1]
                await state.update_data(
                    paths=paths
                )
                await callback.message.answer("Введите номер пути, который вы хотите добавить")
            case "cache_req":
                await state.clear()
                await state.set_state(MStates.CacheRequest.get_name)
                await state.update_data(params=callback_data.params)
                await callback.message.answer("Введите имя, которое вы хотите дать пути")
            case _:
                pass
        await callback.answer()

    @dp.message(MStates.Menu.just_menu, F.text.casefold() == "запрос")
    async def button_req(message: Message, state: FSMContext):
        """
        Начало обработки запроса расписания, переход к запросу станций.
        """
        await state.clear()
        await state.set_state(MStates.Request.get_st_from)
        await state.update_data(req=CacheRequest(None, None, '-',
                                                 *DBUser.user_params(message.from_user.id)[1:],
                                                 is_mlt=False, user_id=message.from_user.id),
                                action='req')
        await message.answer(
            text="Введите станцию(ии) отправления",
            reply_markup=req_args.stations()
        )

    @dp.message(MStates.Request.get_st_from)
    @dp.message(MStates.Request.get_st_to)
    async def button_st(message: Message, state: FSMContext):
        """
        Запрос станций, переход к параметрам запроса.
        Определение, является ли запрос мультистанцевым.
        """
        st: str = message.text.strip()
        st: list[str | Station] = [st] if st.count(' ') == 0 else st.split()
        req: CacheRequest = (await state.get_data())['req']
        if len(st) != 1:
            req.is_mlt = True
            await state.update_data(req=req)
        for ind, station in enumerate(st):
            if check_station(station):
                await state.clear()
                await state.set_state(MStates.Menu.just_menu)
                await message.answer(check_station(station),
                                     reply_markup=menu.menu(*bl_get_nearest_cache_req(message.from_user.id)))
                return
            if not DBStation.station_exists(
                    model.model.get_station(station)
            ):
                DBStation.station_create(model.model.get_station(station))

            st[ind] = model.model.get_station(station)

        if (await state.get_state()) == MStates.Request.get_st_from:
            req.dep_st = st
            await state.update_data(req=req)
            await state.set_state(MStates.Request.get_st_to)
            await message.answer(
                text="Введите станцию(ии) прибытия",
                reply_markup=req_args.stations()
            )
        else:
            req: CacheRequest = (await state.get_data())['req']
            req.arr_st = st
            await state.update_data(req=req)
            await state.set_state(MStates.Request.get_args)
            await message.answer(
                text="Введите параметры",
                reply_markup=req_args.args(req)
            )

    @dp.message(MStates.Request.get_args, F.text.contains("отправления"))
    @dp.message(MStates.Request.get_args, F.text.contains("электричек"))
    @dp.message(MStates.Request.get_args, F.text.contains("сортировки"))
    @dp.message(MStates.Request.get_args, F.text.contains("фильтрации"))
    async def req_get_args(message: Message, state: FSMContext):
        """
        Вызов изменения параметра запроса с определением типа параметра.
        """
        await state.set_state(MStates.Request.change_args)
        val_type: str = ""
        if message.text.__contains__("электричек"):
            val_type = "col"
        elif message.text.__contains__("сортировки"):
            val_type = "sort_type"
        elif message.text.__contains__("фильтрации"):
            val_type = "filter_type"
        elif message.text.__contains__("отправления"):
            val_type = "dep_time"
        await state.update_data(val_type=val_type)
        await message.answer("Укажите желаемое значение", reply_markup=settings_reply.def_val(val_type))

    @dp.message(MStates.Request.change_args)
    async def req_change_args(message: Message, state: FSMContext):
        """
        Изменение параметра state['val_type'] или сообщение о его некорректности.
        """
        val_type = (await state.get_data())["val_type"]
        ans = await bl_parse_change(val_type, message.text.lower())
        req: CacheRequest = (await state.get_data())['req']
        if isinstance(ans, str):
            await message.answer(ans, reply_markup=req_args.args(req))
            await state.set_state(MStates.Request.get_args)
            return
        val_type, val = ans
        req.__setattr__(val_type, val)
        await state.update_data(req=req)
        await state.set_state(MStates.Request.get_args)
        await message.answer("Ваше значение успешно изменено",
                             reply_markup=req_args.args(req))

    @dp.message(MStates.Request.get_args, F.text.casefold() == "сделать запрос")
    async def button_make_req(message: Message, state: FSMContext):
        """
        Вызов запроса с определением цели:

        - Простое расписание

        - Закешировать запрос

        - Закешировать маршрут
        """
        req: CacheRequest = (await state.get_data())['req']
        action = (await state.get_data())['action']
        await state.clear()
        if action == 'cache':
            DBCacheReq.cache_req_create(req)
            await message.answer("Ваш запрос сохранён!",
                                 reply_markup=menu.menu(*bl_get_nearest_cache_req(message.from_user.id)))
        elif action == "req":
            f = bl_mlt_req if req.is_mlt else bl_req
            ans = await f(message.from_user.id, req.get_params())

            await message.answer(ans,
                                 reply_markup=req_inline.req_inline(req.get_params(),
                                                                    logic.req.paths_ids(req)),
                                 parse_mode=ParseMode.MARKDOWN_V2)
            await message.answer("Меню",
                                 reply_markup=menu.menu(*bl_get_nearest_cache_req(message.from_user.id)),
                                 parse_mode=ParseMode.MARKDOWN_V2)
        elif action == "cache_path":
            ans = await cache_path(message.from_user.id, req.get_params())

            await message.answer(ans[0],
                                 reply_markup=req_inline.req_inline(req.get_params(),
                                                                    logic.req.paths_ids(req)),
                                 parse_mode=ParseMode.MARKDOWN_V2)
            await message.answer("Выведите номер пути, который хотите добавить",
                                 reply_markup=menu.menu(*bl_get_nearest_cache_req(message.from_user.id)),
                                 parse_mode=ParseMode.MARKDOWN_V2)

            await state.set_state(MStates.CachePath.get_path)
            await state.update_data(paths=ans[1])
            return

        await state.set_state(MStates.Menu.just_menu)
