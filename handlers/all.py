from aiogram import types
import random
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
import traceback
from states import State
import keyboards as kb
import wb_api
import redis_db
import texts
import gpt_generator
import diagnostics
import datetime
from loader import dp, bot
import config_io
import utils
import sys
if sys.argv[1] == "btl":
    import google_sheets_btl as google_sheets
elif sys.argv[1] == "rastr":
    import google_sheets_rastr as google_sheets


@dp.message_handler(lambda message: str(message.from_user.id) in config_io.get_value('ADMINS'), commands=['start'], state="*")
async def send_welcome(message: types.Message):
    await message.answer(texts.back_to_menu)
    print(message)


@dp.message_handler(commands=['diagnostics'], state="*")
async def send_welcome(message: types.Message):
    await message.answer(texts.diagnos_wait)
    proxy_check = diagnostics.check_proxy(config_io.get_value('PROXY'))
    openai_check = diagnostics.check_openai_via_proxy(config_io.get_value('PROXY'), config_io.get_value('GPT_KEY'))
    wb_ooo_check = diagnostics.check_wb(config_io.get_value('WB_TOKEN_OOO'))
    wb_ip_check = diagnostics.check_wb(config_io.get_value('WB_TOKEN_IP'))
    await message.answer(texts.diagnos_result(proxy_check, openai_check, [wb_ooo_check, wb_ip_check]))


    
@dp.message_handler(lambda message: str(message.from_user.id) in config_io.get_value('ADMINS'), commands=['test'], state="*")
async def send_welcome(message: types.Message):
    feedback_to_test = message.get_args()
    if not feedback_to_test:
        await message.answer('Пустой отзыв. Используйте как /test + отзыв в одном сообщении')
    try:
        answer, total_tokens_used = gpt_generator.get_reply(feedback_to_test)
    except Exception as e:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print('EXCEPTION /test from the bot')
            print(ts)
            print(traceback.format_exc())
            await message.answer(texts.error_alert)
    await message.answer(answer + f'\n\n<i>Суммарно использовано {total_tokens_used}</i>')


@dp.message_handler(lambda message: str(message.from_user.id) in config_io.get_value('ADMINS'), commands=['set_automod'], state="*")
async def send_welcome(message: types.Message):
    selected_rates = redis_db.get_selected_rates()
    await message.answer(texts.automod_changing, reply_markup=kb.get_automod_kb(selected_rates))
    await State.choosing_automod.set()


@dp.callback_query_handler(lambda message: str(message.from_user.id) in config_io.get_value('ADMINS'), state=State.choosing_automod)
async def send_series(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'menu':
        await callback.message.answer(texts.back_to_menu, reply_markup=ReplyKeyboardRemove())
        await state.reset_state(with_data=False)
        return

    tapped_num = int(callback.data)
    selected_numbers = redis_db.get_selected_rates()

    if tapped_num in selected_numbers:
        selected_numbers.remove(tapped_num)
    else:
        selected_numbers.append(tapped_num)

    try:
        await bot.edit_message_reply_markup(callback.message.chat.id,
                            callback.message.message_id,
                            reply_markup=kb.get_automod_kb(selected_numbers))
    except:
        print('Фейл во время попытки изменить клавиатуру с кодом')
    redis_db.set_selected_rates(selected_numbers)
    await bot.answer_callback_query(callback.id)
    

@dp.message_handler(lambda message: str(message.from_user.id) in config_io.get_value('ADMINS'), commands=['logs'], state="*")
async def send_welcome(message: types.Message):
    await message.answer_document(types.InputFile("nohup.out"))



@dp.callback_query_handler(state='*')
async def send_series(callback: types.CallbackQuery):
    tapped = callback.data
    message_id = callback.message.message_id

    all = redis_db.get_all_redis()
    item_to_ans = None
    for item in all:
        if item['reply_message_id'] == message_id:
            item_to_ans = item
            break

    if item_to_ans['account'] == 'OOO':
        auth = config_io.get_value('WB_TOKEN_OOO')
    elif item_to_ans['account'] == 'IP':
        auth = config_io.get_value('WB_TOKEN_IP')

    if tapped == 'sent':

        # not found in redis
        if item_to_ans is None:
            try:
                await bot.edit_message_reply_markup(config_io.get_value('GROUP_ID'), message_id, reply_markup=kb.error_kb)
            except Exception as e:
                print('Ошибка при изменении кнопки')
            await bot.answer_callback_query(callback.id, text='Ошибка при поиске отзыва')
            return
        

        # already answered
        wb_feedback = wb_api.get_feedback_by_id(auth, item_to_ans['feedback_id'])
        if wb_feedback.json()['data']['answer'] is not None:
            try:
                await bot.edit_message_reply_markup(config_io.get_value('GROUP_ID'), message_id, reply_markup=kb.done_by_hand)
            except Exception as e:
                print('уже отвечено')
            await bot.answer_callback_query(callback.id, text='уже отвечено')
            return
        

        res = wb_api.answer_feedback(auth, item_to_ans['feedback_id'], callback.message.text)
        print(res)
        try:
            await bot.edit_message_reply_markup(config_io.get_value('GROUP_ID'), message_id, reply_markup=kb.done_kb)
        except Exception as e:
            print('Ошибка при изменении кнопки')
    elif tapped == 'regenerate':
        await bot.answer_callback_query(callback.id, text='Подождите')
        wb_feedback = wb_api.get_feedback_by_id(auth, item_to_ans['feedback_id']).json().get('data')
        parsed_feedback = utils.parse_feedback(wb_feedback)

        if sys.argv[1] == "btl":
            recs = google_sheets.get_recommendations(wb_feedback['productDetails']['supplierArticle'])
        elif sys.argv[1] == "rastr":
            recs = google_sheets.get_recommendations(wb_feedback['productDetails']['nmId'])
        if recs:
            recs = random.choice(recs)
        reply_gpt, total_used_tokens = gpt_generator.get_reply(parsed_feedback, recs)

        await bot.edit_message_text(reply_gpt + f'\n\n<i>Суммарно использовано {total_used_tokens}</i>', config_io.get_value('GROUP_ID'), message_id, reply_markup=kb.to_send_kb)
    try:
        await bot.answer_callback_query(callback.id)
    except Exception as e:
        print(e)


