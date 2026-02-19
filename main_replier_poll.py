import time
import gpt_generator
import bot_outer_interface
import random
import utils
import keyboards as kb
import redis_db
import traceback
from datetime import datetime
import texts
import config_io
import sys
import ozon_api
if sys.argv[1] == "btl":
    import google_sheets_btl as google_sheets
elif sys.argv[1] == "rastr":
    import google_sheets_rastr as google_sheets


DISABLE_TIMEOUT = 5
FEEDBACK_TIMEOUT = 40
LOCAL_TIMEOUT = 20
EXCEPTION_TIMEOUT = 140


if __name__ == '__main__':
    bot_outer_interface.send_text_message('Начали')
    i = 0
    while True:

        try:
            is_enable = config_io.get_value('ON')
            if not is_enable:
                time.sleep(DISABLE_TIMEOUT)
                continue

            redis_db.delete_old_items()

            auth = config_io.get_value('OZON_TOKEN')
            response_feedbacks = ozon_api.get_feedbacks(auth)
            
            for feedback in response_feedbacks.json()['reviews']:
                if not feedback['text']:
                    continue
                
                if not utils.is_fresher_than_days(feedback['published_at'], 14):
                    continue
                answered = redis_db.get_all_redis()
                to_skip = False
                for item in answered:
                    if feedback['id'] == item['feedback_id']:
                        to_skip = True
                if to_skip:
                    continue
                
                product_info = ozon_api.get_product_info(auth, feedback['sku']).json()['items'][0]
                parsed_feedback = utils.parse_feedback(feedback, product_info)
                message_to_send = utils.compose_message(feedback, product_info)

                message_id = bot_outer_interface.send_text_message(message_to_send)

                # if sys.argv[1] == "btl":
                #     recs = google_sheets.get_recommendations(feedback['sku'])
                # elif sys.argv[1] == "rastr":
                #     recs = google_sheets.get_recommendations(feedback['sku'])

                # if recs:
                #     recs = random.choice(recs)
                reply_gpt, total_used_tokens = gpt_generator.get_reply(parsed_feedback)
                reply_id = bot_outer_interface.send_text_message(reply_gpt + f'\n\n<i>Суммарно использовано {total_used_tokens}</i>', kb.to_send_kb)

                redis_db.add_redis({'timestamp': int(time.time()),
                                'feedback_id': feedback['id'],
                                'account': 'OZON',
                                'message_id': message_id,
                                'reply_message_id': reply_id})
                
                rates_to_auto_reply = redis_db.get_selected_rates()
                if (parsed_feedback['rating'] is not None) and int(parsed_feedback['rating']) in rates_to_auto_reply:
                    ozon_api.answer_feedback(auth, feedback['id'], reply_gpt)
                    bot_outer_interface.edit_kb(reply_id, kb.done_auto_kb)
                

                time.sleep(LOCAL_TIMEOUT)
            time.sleep(FEEDBACK_TIMEOUT)
        except Exception as e:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print('EXCEPTION MAIN_REPLIER')
            print(ts)
            print(traceback.format_exc())
            bot_outer_interface.send_text_message(texts.error_alert)
            time.sleep(EXCEPTION_TIMEOUT)
        


