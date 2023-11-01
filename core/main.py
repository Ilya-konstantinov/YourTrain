import datetime
import logging
import asyncio
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, BufferedInputFile, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.config import TOKEN, ADMIN_CHAT_ID
from FSMachines import MStates
from database.dataframe import DB
from handler.service import bl_set, bl_help, bl_start, bl_del_user_info, bl_recache_user
from handler.req import bl_req, bl_mlt_req, bl_all_req, check_station
from handler.cache_req import new_cache_req, get_cache_req
from handler.cache_path import cache_path, num_path, refr_sched
from handler.config_json import get_json
from model import arg_format
from callback.req import ReqCallbackFactory
from model.path import beauty_time
import keyboard

# Bad logic (:
from data.answer_enums import COMMENT, EDUC

logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
dp = Dispatcher()
user_cache_path: dict[int, list]


@dp.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    user_exists = DB.user_exist(user.id)

    if not user_exists:
        DB.user_create(user.id, user.first_name, message.chat.id)

    ans = await bl_start(user_id=user.id, user_exists=user_exists)
    await message.answer(ans)
    await message.answer(EDUC.CLASSIC)


@dp.message(Command("educ"))
async def cmd_educ(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer(EDUC.CLASSIC)
    else:
        await message.answer(EDUC.WHOLE)


@dp.message(Command("path_cache"))
async def cmd_path_cache(message: Message, command: CommandObject, state: FSMContext):
    await state.set_state(MStates.CachePath.get_path)
    ans = await cache_path(message.from_user.id, command.args)
    await message.answer(ans + "\nВыведите номер пути, который хотите добавить\n⠀", parse_mode=ParseMode.MARKDOWN_V2)


@dp.message(MStates.CachePath.get_path)
async def path_num(message: Message, state: FSMContext):
    await state.set_state(MStates.CachePath.num_path)
    ans = await num_path(message.from_user.id, message.text)
    await message.answer(ans)


@dp.message(Command("help"))
async def cmd_help(message: Message, command: CommandObject):
    ans = await bl_help(user_id=message.from_user.id, args=command.args)
    await message.answer(ans)


@dp.message(Command("multi_req", "mltreq"))
async def mlt_req(message: Message, command: CommandObject):
    ans = await bl_mlt_req(user_id=message.from_user.id, args=command.args)
    await message.answer(ans, parse_mode=ParseMode.MARKDOWN_V2)


@dp.message(Command("set"))
async def set_par(message: Message, command: CommandObject):
    ans = await bl_set(user_id=message.from_user.id, args=command.args)
    await message.answer(ans)


@dp.message(Command("cache"))
async def cache(message: Message, command: CommandObject):
    ans = await new_cache_req(user_id=message.from_user.id, args=command.args)
    await message.answer(ans)


@dp.message(Command("get"))
async def get_cache(message: Message, command: CommandObject):
    ans = await get_cache_req(message.from_user.id, command.args)
    await message.answer(ans, parse_mode=ParseMode.MARKDOWN_V2)


@dp.message(Command("json"))
async def get_cache(message: Message, command: CommandObject):
    json: str = await get_json(message.from_user.id)
    await message.reply_document(BufferedInputFile(json.encode(), filename="config.json"), caption="config.json")


@dp.message(Command("del"))
async def user_del(message: Message, command: CommandObject):
    ans = await bl_del_user_info(message.from_user.id, message.from_user.first_name)
    await message.answer(ans)


@dp.message(Command("recache_user"))
async def cmd_recache_user(message: Message, command: CommandObject):
    ans = await bl_recache_user(message.from_user.id, message.from_user.first_name)
    await message.answer(ans)


@dp.message(Command("req"))
async def cmd_req(message: Message, command: CommandObject):
    ans = await bl_req(user_id=message.from_user.id, args=command.args)
    if ans[0] != '`':
        await message.answer(ans)
        return

    builder = InlineKeyboardBuilder()
    builder.button(
        text="Повторить запрос",
        callback_data=ReqCallbackFactory(action="req", params=command.args.replace(":", '..'))
    )
    builder.button(
        text="Сохранить маршрут",
        callback_data=ReqCallbackFactory(action="cache", params=command.args.replace(":", '..'))
    )

    await message.answer(
        text=ans + '\n⠀',
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=builder.as_markup()
    )


@dp.callback_query(ReqCallbackFactory.filter())
async def callbacks_num_change_fab(
        callback: CallbackQuery,
        callback_data: ReqCallbackFactory,
        state: FSMContext
):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Повторить запрос",
        callback_data=ReqCallbackFactory(action="req", params=callback_data.params)
    )
    builder.button(
        text="Сохранить маршрут",
        callback_data=ReqCallbackFactory(action="cache", params=callback_data.params)
    )

    match callback_data.action:
        case "req":
            await callback.message.answer(
                text=await bl_req(callback.from_user.id, callback_data.params),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=builder.as_markup()
            )
        case "cache":
            await state.set_state(MStates.CachePath.get_path)
            await cache_path(callback.from_user.id, callback_data.params)
            await callback.message.answer("Введите номер пути, который вы хотите добавить")
        case _:
            pass
    await callback.answer()


@dp.message(Command('menu'))
async def cmd_menu(message: Message, state: FSMContext):
    await state.set_state(MStates.Menu.just_menu)
    await message.answer(text="Вот твое меню ссаное", reply_markup=(menu.menu()))


@dp.message(MStates.Menu.just_menu, F.text.casefold() == 'отзыв')
async def reply_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(MStates.Comment.get_args)
    await message.answer("ХУЙ", reply_markup=menu.comment_args())


@dp.message(MStates.Comment.get_args)
async def get_comment_args(message: Message, state: FSMContext) -> None:
    await state.set_state(MStates.Comment.set_comment)
    await state.update_data(is_anon=(message.text.lower() == "анонимно"))
    await message.answer(COMMENT.GET_ARGS, reply_markup=ReplyKeyboardRemove())


@dp.message(MStates.Comment.set_comment)
async def send_comment(message: Message, state: FSMContext, bot: Bot):
    is_anon = (await state.get_data()).get("is_anon")
    if is_anon:
        sender = "Анонимен"
    else:
        sender = f"id: {message.from_user.id}\nname: {message.from_user.full_name}"

    await state.clear()
    ans = COMMENT.SUCCESS_F.format((is_anon in ['0', "не анонимно"]) * "не ")
    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=COMMENT.TO_ADMIN_F.format(sender, message.text)
        )
    except:
        await message.answer(COMMENT.UNSUCCESSFUL)
        return

    await state.set_state(MStates.Menu.just_menu)
    await message.answer(ans, reply_markup=menu.menu())


@dp.message(Command("cancel"))
@dp.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(Command("all_req"))
@dp.message(MStates.Menu.just_menu, F.text.casefold() == "сохранённые запросы")
async def cmd_all_req(message: Message):
    ans = await bl_all_req(message.from_user.id)
    await message.answer(ans,
                         parse_mode=ParseMode.MARKDOWN_V2,
                         reply_markup=menu.cache_req_inline(DB.cache_req_whole_get(message.from_user.id)))


@dp.message(MStates.Menu.just_menu, F.text.casefold() == "запрос")
async def button_req(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(MStates.Request.get_st_from)
    await message.answer(
        text="Введите станцию(ии) отправления",
        reply_markup=keyboard.req_args.stations()
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
            reply_markup=keyboard.req_args.stations()
        )
    else:
        await state.update_data(st_to=st)
        if not isinstance(st, str):
            await state.update_data(is_mlt=True)
        dep_time_raw: datetime = datetime.datetime.now()
        dep_time = beauty_time(dep_time_raw)
        sort_type, filter_type, col = DB.user_params(message.from_user.id)
        args = (dep_time, sort_type, filter_type, col)
        await state.set_state(MStates.Request.get_args)
        await state.update_data(dep_time=dep_time,
                                sort_type=sort_type,
                                filter_type=filter_type,
                                col=col)
        await message.answer(
            text="Введите станцию(ии) прибытия",
            reply_markup=keyboard.req_args.args(*args)
        )


@dp.message(MStates.Request.get_args, F.text.contains("отправления"))
async def button_time(message: Message, state: FSMContext):
    if isinstance(arg_format.time_arg(message.text), str):
        args = await state.get_data()
        args = (args["dep_time"], args["sort_type"], args["filter_type"], args["col"])
        await state.set_state(MStates.Request.get_args)
        await message.answer(arg_format.time_arg(message.text),
                             reply_markup=keyboard.req_args.args(*args))
    else:
        await state.update_data(dep_time=message.text)
        await state.set_state(MStates.Request.get_args)
        args = await state.get_data()
        args = (args["dep_time"], args["sort_type"], args["filter_type"], args["col"])
        await message.answer("Время отправления установлено",
                             reply_markup=keyboard.req_args.args(*args))


@dp.message(MStates.Request.get_args, F.text.contains("электричек"))
async def button_col(message: Message, state: FSMContext):
    col = arg_format.col_arg(message.text)
    if isinstance(col, str):
        args = await state.get_data()
        args = (args["dep_time"], args["sort_type"], args["filter_type"], args["col"])
        await state.set_state(MStates.Request.get_args)
        await message.answer(arg_format.time_arg(message.text),
                             reply_markup=keyboard.req_args.args(*args))
    else:
        await state.update_data(col=col)
        await state.set_state(MStates.Request.get_args)
        args = await state.get_data()
        args = (args["dep_time"], args["sort_type"], args["filter_type"], args["col"])
        await message.answer("Количество электричек установлено",
                             reply_markup=keyboard.req_args.args(*args))


@dp.message(MStates.Request.get_args, F.text.contains("сортировки"))
async def button_sort(message: Message, state: FSMContext):
    sort_type = arg_format.sort_arg(message.text)
    if isinstance(sort_type, str):
        args = await state.get_data()
        args = (args["dep_time"], args["sort_type"], args["filter_type"], args["col"])
        await state.set_state(MStates.Request.get_args)
        await message.answer(arg_format.time_arg(message.text),
                             reply_markup=keyboard.req_args.args(*args))
    else:
        await state.update_data(sort_type=sort_type)
        await state.set_state(MStates.Request.get_args)
        args = await state.get_data()
        args = (args["dep_time"], args["sort_type"], args["filter_type"], args["col"])
        await message.answer("Тип сортировки установлен",
                             reply_markup=keyboard.req_args.args(*args))


@dp.message(MStates.Request.get_args, F.text.contains("фильтрации"))
async def button_filter(message: Message, state: FSMContext):
    filter_type = arg_format.filter_arg(message.text)
    if isinstance(filter_type, str):
        args = await state.get_data()
        args = (args["dep_time"], args["sort_type"], args["filter_type"], args["col"])
        await state.set_state(MStates.Request.get_args)
        await message.answer(arg_format.time_arg(message.text),
                             reply_markup=keyboard.req_args.args(*args))
    else:
        await state.update_data(filter_type=filter_type)
        await state.set_state(MStates.Request.get_args)
        args = await state.get_data()
        args = (args["dep_time"], args["sort_type"], args["filter_type"], args["col"])
        await message.answer("Тип сортировки установлен",
                             reply_markup=keyboard.req_args.args(*args))


async def bot_start(bot) -> None:
    await dp.start_polling(bot)


async def main() -> None:
    bot = Bot(token=TOKEN)
    await asyncio.gather(bot_start(bot), refr_sched(bot))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
