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


@dp.message_handler(lambda message: str(message.from_user.id) in config_io.get_value('ADMINS'),commands=['get_settings'], state="*")
async def send_welcome(message: types.Message):
    to_answer = f"""<b>Нынешняя конфигурация настроек</b>\n\n
Токен ООО: {utils.short_tail(config_io.get_value('WB_TOKEN_OOO'))}
Токен ИП: {utils.short_tail(config_io.get_value('WB_TOKEN_IP'))}
Прокси: {utils.short_tail(config_io.get_value('PROXY'))}
Токен openAI: {utils.short_tail(config_io.get_value('GPT_KEY'))}
Id группы: {utils.short_tail(config_io.get_value('GROUP_ID'))}\n\n"""
    await message.answer(to_answer)


@dp.message_handler(lambda message: str(message.from_user.id) in config_io.get_value('ADMINS'),commands=['set_openai'], state="*")
async def send_welcome(message: types.Message):
    await message.answer(f"Токен openAI: {utils.short_tail(config_io.get_value('GPT_KEY'))}")
    await message.answer(texts.change_setting, reply_markup=kb.cancel_kb)
    await State.changing_openai.set()

@dp.message_handler(lambda message: str(message.from_user.id) in config_io.get_value('ADMINS'),state=State.changing_openai)
async def send_welcome(message: types.Message, state: FSMContext):
    if message.text.lower().strip() == buttons.cancel.lower().strip():
        await message.answer(texts.instructions_change_canceled)
        await message.answer(texts.back_to_menu, reply_markup=ReplyKeyboardRemove())
    elif message.text:
        config_io.update_key('GPT_KEY', message.text.strip())
        await message.answer(texts.success_instruction_change)
        await message.answer(texts.back_to_menu, reply_markup=ReplyKeyboardRemove())
    await state.reset_state(with_data=False)


@dp.message_handler(lambda message: str(message.from_user.id) in config_io.get_value('ADMINS'),commands=['set_group_id'], state="*")
async def send_welcome(message: types.Message):
    await message.answer(f"id группы: {utils.short_tail(config_io.get_value('GROUP_ID'))}")
    await message.answer(texts.change_setting, reply_markup=kb.cancel_kb)
    await State.changing_group.set()

@dp.message_handler(lambda message: str(message.from_user.id) in config_io.get_value('ADMINS'),state=State.changing_group)
async def send_welcome(message: types.Message, state: FSMContext):
    if message.text.lower().strip() == buttons.cancel.lower().strip():
        await message.answer(texts.instructions_change_canceled)
        await message.answer(texts.back_to_menu, reply_markup=ReplyKeyboardRemove())
    elif message.text:
        config_io.update_key('GROUP_ID', message.text.strip())
        await message.answer(texts.success_instruction_change)
        await message.answer(texts.back_to_menu, reply_markup=ReplyKeyboardRemove())
    await state.reset_state(with_data=False)


@dp.message_handler(lambda message: str(message.from_user.id) in config_io.get_value('ADMINS'),commands=['set_proxy'], state="*")
async def send_welcome(message: types.Message):
    await message.answer(f"Прокси: {utils.short_tail(config_io.get_value('PROXY'))}")
    await message.answer(texts.change_setting, reply_markup=kb.cancel_kb)
    await State.changing_proxy.set()

@dp.message_handler(lambda message: str(message.from_user.id) in config_io.get_value('ADMINS'),state=State.changing_proxy)
async def send_welcome(message: types.Message, state: FSMContext):
    if message.text.lower().strip() == buttons.cancel.lower().strip():
        await message.answer(texts.instructions_change_canceled)
        await message.answer(texts.back_to_menu, reply_markup=ReplyKeyboardRemove())
    elif message.text:
        proxy_to_set = message.text
        if not 'http://' in message.text:
            proxy_to_set = 'http://' + message.text
        if utils.is_valid_proxy(proxy_to_set):
            config_io.update_key('PROXY', message.text.strip())
            await message.answer(texts.success_instruction_change)
        else:
            await message.answer('ошибка, прокси должны быть вида http://логин:пароль@ip:порт')
        await message.answer(texts.back_to_menu, reply_markup=ReplyKeyboardRemove())
    await state.reset_state(with_data=False)


@dp.message_handler(lambda message: str(message.from_user.id) in config_io.get_value('ADMINS'),commands=['set_wb_ooo'], state="*")
async def send_welcome(message: types.Message):
    await message.answer(f"Токен вб ООО: {utils.short_tail(config_io.get_value('WB_TOKEN_OOO'))}")
    await message.answer(texts.change_setting, reply_markup=kb.cancel_kb)
    await State.changing_wb_ooo.set()

@dp.message_handler(lambda message: str(message.from_user.id) in config_io.get_value('ADMINS'),state=State.changing_wb_ooo)
async def send_welcome(message: types.Message, state: FSMContext):
    if message.text.lower().strip() == buttons.cancel.lower().strip():
        await message.answer(texts.instructions_change_canceled)
        await message.answer(texts.back_to_menu, reply_markup=ReplyKeyboardRemove())
    elif message.text:
        config_io.update_key('WB_TOKEN_OOO', message.text.strip())
        await message.answer(texts.success_instruction_change)
        await message.answer(texts.back_to_menu, reply_markup=ReplyKeyboardRemove())
    await state.reset_state(with_data=False)


@dp.message_handler(lambda message: str(message.from_user.id) in config_io.get_value('ADMINS'), commands=['set_wb_ip'], state="*")
async def send_welcome(message: types.Message):
    await message.answer(f"Токен вб ИП: {utils.short_tail(config_io.get_value('WB_TOKEN_IP'))}")
    await message.answer(texts.change_setting, reply_markup=kb.cancel_kb)
    await State.changing_wb_ip.set()

@dp.message_handler(lambda message: str(message.from_user.id) in config_io.get_value('ADMINS'), state=State.changing_wb_ip)
async def send_welcome(message: types.Message, state: FSMContext):
    if message.text.lower().strip() == buttons.cancel.lower().strip():
        await message.answer(texts.instructions_change_canceled)
        await message.answer(texts.back_to_menu, reply_markup=ReplyKeyboardRemove())
    elif message.text:
        config_io.update_key('WB_TOKEN_IP', message.text.strip())
        await message.answer(texts.success_instruction_change)
        await message.answer(texts.back_to_menu, reply_markup=ReplyKeyboardRemove())
    await state.reset_state(with_data=False)


