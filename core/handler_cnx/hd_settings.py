from aiogram import Dispatcher, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile, ReplyKeyboardRemove

from FSMachines import MStates
from data.answer_enums import COMMENT
from data.config import ADMIN_CHAT_ID
from database.db_cache_req import DBCacheReq
from database.db_user import DBUser
from keyboard import comment
from keyboard import menu
from keyboard import settings_reply
from logic.config_json import get_json
from logic.service import bl_set, bl_del_user_info, bl_get_nearest_cache_req, bl_recache_user


def hand(dp: Dispatcher):
    """
    Внесение функций в хендлер
    """
    @dp.message(Command("set"))
    async def set_par(message: Message, command: CommandObject):
        """
        Изменяет какой-либо параметр по умолчанию для пользователя или возвращает сообщение о некорректности запроса.
        """
        ans = await bl_set(user_id=message.from_user.id, args=command.args)
        await message.answer(ans)

    @dp.message(Command("json"))
    async def get_cache(message: Message):
        """
        Возвращает json настроек пользователя.
        """
        json: str = await get_json(message.from_user.id)
        await message.reply_document(BufferedInputFile(json.encode(), filename="config.json"), caption="config.json")

    @dp.message(Command("del"))
    async def user_del(message: Message):
        """
        Полностью удаляет информацию о сохранённых путях и запросах пользователя, а его настройки меняет на стандартные.
        """
        ans = await bl_del_user_info(message.from_user.id, message.from_user.first_name)
        await message.answer(ans)

    @dp.message(MStates.Menu.just_menu, F.text.casefold() == 'настройки')
    async def set_start(message: Message, state: FSMContext):
        """
        Переход от стандартного меню к меню настроек.
        """
        await state.set_state(MStates.Settings.just_settings)
        param = DBUser.user_params(message.from_user.id)[1:]
        await message.answer(text="Меню настроек", reply_markup=settings_reply.give(*param))

    @dp.message(MStates.Settings.just_settings, F.text.casefold() == 'отзыв')
    async def reply_command(message: Message, state: FSMContext) -> None:
        """
        Вызов принятия аргументов анонимности для отзыва адину.
        """
        await state.clear()
        await state.set_state(MStates.Comment.get_args)
        await message.answer("Как вы хотите оставить отзыв?", reply_markup=comment.comment_args())

    @dp.message(MStates.Comment.get_args)
    async def get_comment_args(message: Message, state: FSMContext) -> None:
        """
        Принимает параметры анонимности для отзыва.
        """
        await state.set_state(MStates.Comment.set_comment)
        await state.update_data(is_anon=(message.text.lower() == "анонимно"))
        await message.answer(COMMENT.GET_ARGS, reply_markup=ReplyKeyboardRemove())

    @dp.message(MStates.Comment.set_comment)
    async def send_comment(message: Message, state: FSMContext, bot: Bot):
        """
        Отсылает админу бота отзыв пользователя анонимно или не анонимно.
        """
        is_anon = (await state.get_data()).get("is_anon")
        if is_anon:
            sender = "Анонимен"
        else:
            sender = f"id: {message.from_user.id}\nname: {message.from_user.full_name}"

        await state.clear()
        ans = COMMENT.SUCCESS_F.format((not is_anon) * "не ")
        try:
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=COMMENT.TO_ADMIN_F.format(sender, message.text)
            )
        except:
            await message.answer(COMMENT.UNSUCCESSFUL)
            return

        await state.set_state(MStates.Menu.just_menu)
        await message.answer(ans, reply_markup=menu.menu(
            *bl_get_nearest_cache_req(message.from_user.id)
        ))

    @dp.message(MStates.Settings.just_settings, F.text.casefold() == 'сбросить')
    async def set_recache_user(message: Message):
        """
        Сбрасывает параметры пользователя на параметры по умолчанию.
        """
        ans = await bl_recache_user(message.from_user.id, message.from_user.first_name)
        await message.answer(ans, reply_markup=settings_reply.give(*DBUser.user_params(message.from_user.id)[1:]))

    @dp.message(MStates.Settings.just_settings, F.text.casefold() == 'скачать')
    async def set_recache_user(message: Message):
        """
        Возвращает json настроек пользователя.
        """
        json: str = await get_json(message.from_user.id)
        await message.reply_document(BufferedInputFile(json.encode(), filename="config.json"), caption="config.json",
                                     reply_markup=settings_reply.give(*DBUser.user_params(message.from_user.id)[1:]))

    @dp.message(MStates.Settings.just_settings, F.text.casefold() == 'очистить полностью')
    async def set_del(message: Message):
        """
        Полностью удаляет информацию о сохранённых путях и запросах пользователя, а его настройки меняет на стандартные.
        """
        ans = await bl_del_user_info(message.from_user.id, message.from_user.first_name)
        await message.answer(ans, reply_markup=settings_reply.give(*DBUser.user_params(message.from_user.id)[1:]))

    @dp.message(MStates.Settings.just_settings, F.text.casefold() == 'обратно')
    async def set_back(message: Message, state: FSMContext):
        """
        Возвращение пользователя к стандартному меню.
        """
        await state.clear()
        await state.set_state(MStates.Menu.just_menu)
        await message.answer("Возвращаю", reply_markup=menu.menu(
            *DBCacheReq.get_nearest(message.from_user.id)
        ))

    @dp.message(MStates.Settings.just_settings, F.text.contains("электричек"))
    @dp.message(MStates.Settings.just_settings, F.text.contains("сортировки"))
    @dp.message(MStates.Settings.just_settings, F.text.contains("фильтрации"))
    @dp.message(MStates.Settings.just_settings, F.text.casefold() == "имя")
    async def set_set(message: Message, state: FSMContext):
        """
        Изменение какого-либо параметра по умолчанию.
        """
        await state.set_state(MStates.Settings.change_def)
        val_type: str = ""
        if message.text.__contains__("электричек"):
            val_type = "col"
        elif message.text.__contains__("сортировки"):
            val_type = "sort_type"
        elif message.text.__contains__("фильтрации"):
            val_type = "filter_type"
        elif message.text.__contains__("Имя"):
            val_type = "name"
        await state.update_data(val_type=val_type)
        await message.answer("Укажите желаемое значение", reply_markup=settings_reply.def_val(val_type))

    @dp.message(MStates.Settings.change_def, F.text.casefold() == "обратно")
    async def set_set_def(message: Message, state: FSMContext):
        """
        Возвращает пользователя в меню настроек.
        """
        await state.clear()
        await state.set_state(MStates.Settings.just_settings)
        await message.answer("Возвращаю", reply_markup=settings_reply.give(
            *DBUser.user_params(message.from_user.id)[1:]
        ))

    @dp.message(MStates.Settings.change_def)
    async def set_def(message: Message, state: FSMContext):
        """
        Изменяет какой-либо парамер пользователя или возвращает сообщение о его некорректности.
        """
        ans = await bl_set(message.from_user.id,
                           f'{(await state.get_data())["val_type"]} {message.text.lower()}')
        await message.answer(ans, reply_markup=settings_reply.give(
            *DBUser.user_params(message.from_user.id)[1:]
        ))
        await state.clear()
        await state.set_state(MStates.Settings.just_settings)
