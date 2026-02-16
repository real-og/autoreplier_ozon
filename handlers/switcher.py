from aiogram import types
import config_io
from loader import dp


@dp.message_handler(lambda message: str(message.from_user.id) in config_io.get_value('ADMINS'),commands=['enable'], state="*")
async def send_welcome(message: types.Message):
    await message.answer("Бот включен")
    config_io.update_key('ON', True)


@dp.message_handler(lambda message: str(message.from_user.id) in config_io.get_value('ADMINS'),commands=['disable'], state="*")
async def send_welcome(message: types.Message):
    await message.answer("Бот выключен")
    config_io.update_key('ON', False)