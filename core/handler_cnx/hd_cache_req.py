from aiogram import Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from FSMachines import MStates
from database.db_user import DBUser
from keyboard import cache_req, settings_reply, req_args, menu
from keyboard.req_inline import req_inline
from logic.cache_req import new_cache_req, get_cache_req
from logic.req import bl_all_req, bl_parse_change
from database.db_cache_req import DBCacheReq
from logic.service import bl_get_nearest_cache_req
from model.path import CacheRequest


def hand(dp: Dispatcher):
    @dp.message(Command("cache"))
    async def cache(message: Message, command: CommandObject):
        ans = await new_cache_req(user_id=message.from_user.id, args=command.args)
        await message.answer(ans)

    @dp.message(Command("all_req"))
    @dp.message(MStates.Menu.just_menu, F.text.casefold() == "сохранённые запросы")
    async def cmd_all_req(message: Message, state: FSMContext):
        ans = await bl_all_req(message.from_user.id)
        await state.clear()
        await state.set_state(MStates.CacheReq.just_cache)
        await state.update_data(reqs=DBCacheReq.cache_req_whole_get(message.from_user.id))
        await message.answer(ans,
                             parse_mode=ParseMode.MARKDOWN_V2,
                             reply_markup=cache_req.cache_req_reply(
                                 DBCacheReq.cache_req_whole_get(message.from_user.id)
                             )
                             )

    @dp.message(MStates.CacheReq.just_cache, F.text.casefold() == "изменить")
    @dp.message(MStates.CacheReq.just_cache, F.text.casefold() == "удалить")
    async def change_cached_req(message: Message, state: FSMContext):
        await state.update_data(action="del" if message.text.lower() == "удалить" else "change")
        await message.answer("Введите номер маршрута, который вы хотите изменить", reply_markup=cache_req.schet(
            len((await state.get_data())["reqs"])
        ))
        await state.set_state(MStates.CacheReq.change)

    @dp.message(MStates.CacheReq.change)
    async def del_edit_cached_req(message: Message, state: FSMContext):
        reqs: list = (await state.get_data())["reqs"]
        try:
            num = int(message.text)
            assert 1 <= num <= len(reqs)
        except:
            await state.set_state(MStates.CacheReq.just_cache)
            await message.answer("Вы указали неправильный номер", reply_markup=cache_req.cache_req_reply(reqs))
            return
        req = reqs.pop(num-1)
        DBCacheReq.cache_req_del(req)

        await state.update_data(req=req)
        await state.update_data(reqs=reqs)
        await state.update_data(old_req=req)
        if (await state.get_data())['action'] == "del":
            await message.answer("Вы успешно удалили запрос!", reply_markup=cache_req.cache_req_reply(reqs))
            await state.set_state(MStates.CacheReq.just_cache)
        else:
            await state.set_state(MStates.CacheReq.change_cached)
            await message.answer("Вот ваш запрос", reply_markup=cache_req.change_cached(req))

    @dp.message(MStates.CacheReq.change_cached, F.text.contains("отправления"))
    @dp.message(MStates.CacheReq.change_cached, F.text.contains("электричек"))
    @dp.message(MStates.CacheReq.change_cached, F.text.contains("сортировки"))
    @dp.message(MStates.CacheReq.change_cached, F.text.contains("фильтрации"))
    @dp.message(MStates.CacheReq.change_cached, F.text.contains("Имя"))
    async def cache_recache(message: Message, state: FSMContext):
        val_type: str = ""
        if message.text.__contains__("электричек"):
            val_type = "col"
        elif message.text.__contains__("сортировки"):
            val_type = "sort_type"
        elif message.text.__contains__("фильтрации"):
            val_type = "filter_type"
        elif message.text.__contains__("отправления"):
            val_type = "dep_time"
        elif message.text.__contains__("Имя"):
            val_type = "name"
        else:
            await message.answer("Укажите правильный тип изменения, пожалуйста")

        await state.set_state(MStates.CacheReq.change_args)
        await state.update_data(val_type=val_type)
        await message.answer("Укажите желаемое значение", reply_markup=settings_reply.def_val(val_type))

    @dp.message(MStates.CacheReq.change_cached, F.text.casefold() == "сохранить запрос")
    async def save(message: Message, state: FSMContext):
        req = (await state.get_data())["req"]
        DBCacheReq.cache_req_create(req)
        reqs = (await state.get_data())["reqs"]
        reqs.append(req)
        await state.update_data(reqs=reqs)
        await state.set_state(MStates.CacheReq.just_cache)
        await message.answer("Ваш запрос сохранён", reply_markup=cache_req.cache_req_reply(reqs))

    @dp.message(MStates.CacheReq.change_cached, F.text.casefold() == "отмена")
    async def save(message: Message, state: FSMContext):
        req = (await state.get_data())["old_req"]
        DBCacheReq.cache_req_create(req)
        reqs = (await state.get_data())["reqs"]
        reqs.append(req)
        await state.update_data(reqs=reqs)
        await state.set_state(MStates.CacheReq.just_cache)
        await message.answer("Возвращаю", reply_markup=cache_req.cache_req_reply(reqs))

    @dp.message(MStates.CacheReq.change_args)
    async def req_change_args(message: Message, state: FSMContext):
        val_type = (await state.get_data())["val_type"]
        req: CacheRequest = (await state.get_data())["req"]
        cache_req.change_cached(req)
        ans = await bl_parse_change(val_type, message.text.lower())
        if isinstance(ans, str):
            await message.answer(ans, reply_markup=cache_req.change_cached(req))
            return

        val_type, val = ans
        req.__setattr__(val_type, val)
        await state.update_data(req=req)
        await state.set_state(MStates.CacheReq.change_cached)
        await message.answer("Ваше значение успешно изменено",
                             reply_markup=cache_req.change_cached(req))

    @dp.message(MStates.CacheRequest.get_name)
    async def get_name(message: Message, state: FSMContext):
        name = message.text
        params = (await state.get_data())['params']
        params = name + ' ' + params
        ans = await new_cache_req(message.from_user.id, params)
        await message.answer(ans)

    @dp.message(MStates.CacheReq.just_cache, F.text.casefold() == "отмена")
    async def close(message: Message, state: FSMContext):
        await state.clear()
        await state.set_state(MStates.Menu.just_menu)
        await message.answer("Возвращаю", reply_markup=menu.menu(*DBCacheReq.get_nearest(message.from_user.id)))

    @dp.message(MStates.CacheReq.just_cache, F.text.casefold() == "создать")
    async def create(message: Message, state: FSMContext):
        await state.set_state(MStates.CacheReq.get_name)
        await message.answer("Введите имя желаемого сохранённого запроса")

    @dp.message(MStates.CacheReq.get_name)
    async def get_name(message: Message, state: FSMContext):
        name = message.text
        ans = await bl_parse_change("name", name)
        if isinstance(ans, str):
            await message.answer(ans, reply_markup=cache_req.cache_req_reply(
                DBCacheReq.cache_req_whole_get(message.from_user.id)
            ))
        uid = message.from_user.id
        await state.clear()
        await state.set_state(MStates.Request.get_st_from)
        await state.update_data(req=CacheRequest(None, None, '-',
                                                 *DBUser.user_params(uid)[1:], is_mlt=False,
                                                 user_id=uid, name=name),
                                action='cache')
        await message.answer(
            text="Введите станцию(ии) отправления",
            reply_markup=req_args.stations()
        )

    @dp.message(Command("get"))
    async def get_cache(message: Message, command: CommandObject, state: FSMContext):
        ans = await get_cache_req(message.from_user.id, command.args)
        if ans[0] != '`':
            await message.answer(ans)
            return
        if await state.get_state():
            await state.clear()
        await state.set_state(MStates.Menu.just_menu)
        await message.answer(ans, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=req_inline(message.text))
        await message.answer("Меню", reply_markup=menu.menu(
                *bl_get_nearest_cache_req(message.from_user.id)
            ),)

