from datetime import datetime

from aiogram import Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from FSMachines import MStates
from callback.req import ReqCallbackFactory
from database.db_user import DBUser
from logic.cache_path import cache_path
from logic.req import bl_req, bl_mlt_req, check_station
from keyboard import req_inline, req_args


def hand(dp: Dispatcher):
    @dp.message(Command("req"))
    async def cmd_req(message: Message, command: CommandObject):
        ans = await bl_req(user_id=message.from_user.id, args=command.args)
        if ans[0] != '`':
            await message.answer(ans)
            return

        args = command.args.replace(":", '..')

        await message.answer(
            text=ans + '\n⠀',
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=req_inline.req_inline(args)
        )

    @dp.message(Command("multi_req", "mltreq"))
    async def mlt_req(message: Message, command: CommandObject):
        ans = await bl_mlt_req(user_id=message.from_user.id, args=command.args)
        await message.answer(ans, parse_mode=ParseMode.MARKDOWN_V2)

    @dp.callback_query(ReqCallbackFactory.filter())
    async def callbacks_num_change_fab(
            callback: CallbackQuery,
            callback_data: ReqCallbackFactory,
            state: FSMContext
    ):
        args = callback_data.params
        match callback_data.action:
            case "req":
                await callback.message.answer(
                    text=await bl_req(callback.from_user.id, callback_data.params),
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=req_inline.req_inline(args)
                )
            case "cache_path":
                await state.clear()
                await state.set_state(MStates.CachePath.get_path)
                await cache_path(callback.from_user.id, callback_data.params)
                await callback.message.answer("Введите номер пути, который вы хотите добавить")
            case "cache_req":
                await state.clear()
                await state.set_state(MStates.CacheRequest.get_name)
                await state.update_data(params=callback_data.params)
                await callback.message.answer("Введите имя, которое вы хотите дать пути")
            case _:
                pass
        await callback.answer()

    # Gonna cry ?
    @dp.message(MStates.Menu.just_menu, F.text.casefold() == "запрос")
    async def button_req(message: Message, state: FSMContext):
        await state.clear()
        await state.set_state(MStates.Request.get_st_from)
        await message.answer(
            text="Введите станцию(ии) отправления",
            reply_markup=req_args.stations()
        )

    @dp.message(MStates.Request.get_st_from)
    @dp.message(MStates.Request.get_st_to)
    async def button_req(message: Message, state: FSMContext):
        st: str = message.text.strip()
        st = st if st.count(' ') == 0 else st.split()
        if isinstance(st, str):
            if check_station(st):
                await state.clear()
                await state.set_state(MStates.Menu.just_menu)
                await message.answer(check_station(st))
        else:
            for station in st:
                if check_station(station):
                    await state.clear()
                    await state.set_state(MStates.Menu.just_menu)
                    await message.answer(check_station(station))
        if (await state.get_state()) == MStates.Request.get_st_from:
            await state.update_data(st_from=st)
            if not isinstance(st, str):
                await state.update_data(is_mlt=True)
            await state.set_state(MStates.Request.get_st_to)
            await message.answer(
                text="Введите станцию(ии) прибытия",
                reply_markup=req_args.stations()
            )
        else:
            await state.update_data(st_to=st)
            if not isinstance(st, str):
                await state.update_data(is_mlt=True)
            dep_time = None
            _, sort_type, filter_type, col = DBUser.user_params(message.from_user.id)
            args = (dep_time, sort_type, filter_type, col)
            await state.set_state(MStates.Request.get_args)
            await state.update_data(dep_time=dep_time,
                                    sort_type=sort_type,
                                    filter_type=filter_type,
                                    col=col)
            await message.answer(
                text="Введите станцию(ии) прибытия",
                reply_markup=req_args.args(*args)
            )
