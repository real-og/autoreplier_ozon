from aiogram import types
import config_io
import texts
from loader import dp


@dp.message_handler(lambda message: str(message.from_user.id) in config_io.get_value('ADMINS'), commands=['help'], state="*")
async def send_welcome(message: types.Message):
    await message.answer(texts.help)
