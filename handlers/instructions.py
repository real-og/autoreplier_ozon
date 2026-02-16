from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
import utils
from states import State
import keyboards as kb
import config_io
import texts
import buttons
from loader import dp


@dp.message_handler(commands=['get_instructions'], state="*")
async def send_welcome(message: types.Message):
    to_answer = f"""<b>Нынешние инструкции для нейросети</b>\n
{config_io.get_value('INSTRUCTIONS')}\n"""
    await message.answer(to_answer)


@dp.message_handler(commands=['set_instructions'], state="*")
async def send_welcome(message: types.Message):
    await message.answer(config_io.get_value('INSTRUCTIONS'))
    await message.answer(texts.change_instructions, reply_markup=kb.cancel_kb)
    await State.changing_instructions.set()

@dp.message_handler(state=State.changing_instructions)
async def send_welcome(message: types.Message, state: FSMContext):
    if message.text.lower().strip() == buttons.cancel.lower().strip():
        await message.answer(texts.instructions_change_canceled)
        await message.answer(texts.back_to_menu, reply_markup=ReplyKeyboardRemove())
    elif message.text:
        config_io.update_key('INSTRUCTIONS', message.text.strip())
        await message.answer(texts.success_instruction_change)
        await message.answer(texts.back_to_menu, reply_markup=ReplyKeyboardRemove())
    await state.reset_state(with_data=False)


@dp.message_handler(commands=['get_rec_instructions'], state="*")
async def send_welcome(message: types.Message):
    to_answer = f"""<b>Нынешние инструкции для РЕКОМЕНДАЦИИ нейросети</b>\n
{config_io.get_value('RECOMMEND_INSTRUCTIONS')}\n"""
    await message.answer(to_answer)


@dp.message_handler(commands=['set_rec_instructions'], state="*")
async def send_welcome(message: types.Message):
    await message.answer(config_io.get_value('RECOMMEND_INSTRUCTIONS'))
    await message.answer(texts.change_rec_instructions, reply_markup=kb.cancel_kb)
    await State.changing_rec_instructions.set()

@dp.message_handler(state=State.changing_rec_instructions)
async def send_welcome(message: types.Message, state: FSMContext):
    if message.text.lower().strip() == buttons.cancel.lower().strip():
        await message.answer(texts.instructions_change_canceled)
        await message.answer(texts.back_to_menu, reply_markup=ReplyKeyboardRemove())
    elif message.text:
        config_io.update_key('RECOMMEND_INSTRUCTIONS', message.text.strip())
        await message.answer(texts.success_instruction_change)
        await message.answer(texts.back_to_menu, reply_markup=ReplyKeyboardRemove())
    await state.reset_state(with_data=False)