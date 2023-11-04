from aiogram import Dispatcher, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile, ReplyKeyboardRemove

from FSMachines import MStates
from data.answer_enums import COMMENT
from data.config import ADMIN_CHAT_ID
from logic.config_json import get_json
from logic.service import bl_set, bl_del_user_info, bl_get_nearest_cache_req
from keyboard import comment
from keyboard import menu


def hand(dp: Dispatcher):
    @dp.message(Command("set"))
    async def set_par(message: Message, command: CommandObject):
        ans = await bl_set(user_id=message.from_user.id, args=command.args)
        await message.answer(ans)

    @dp.message(Command("json"))
    async def get_cache(message: Message, command: CommandObject):
        json: str = await get_json(message.from_user.id)
        await message.reply_document(BufferedInputFile(json.encode(), filename="config.json"), caption="config.json")

    @dp.message(Command("del"))
    async def user_del(message: Message, command: CommandObject):
        ans = await bl_del_user_info(message.from_user.id, message.from_user.first_name)
        await message.answer(ans)

    @dp.message(MStates.Menu.just_menu, F.text.casefold() == 'отзыв')
    async def reply_command(message: Message, state: FSMContext) -> None:
        await state.clear()
        await state.set_state(MStates.Comment.get_args)
        await message.answer("Как вы хотите оставить отзыв?", reply_markup=comment.comment_args())

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
        await message.answer(ans, reply_markup=menu.menu(
            bl_get_nearest_cache_req(message.from_user.id)
        ))