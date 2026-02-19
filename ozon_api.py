import requests
import config_io
import utils


BASE_URL = 'https://api-seller.ozon.ru'
client_id = config_io.get_value('CLIENT_ID')


def get_feedbacks(auth):
    url = '/v1/review/list'
    headers = { 'Host': 'api-seller.ozon.ru',
                'Client-Id': client_id,
                'Api-Key': auth,
                'Content-Type': 'application/json',}
    
    body ={'status': 'UNPROCESSED',
             'limit': 100,
             'sort_dir': 'DESC'
            }
    response = requests.post(BASE_URL + url, headers=headers, json=body)
    return response


def get_product_info(auth, sku):
    url = '/v3/product/info/list'
    headers = { 'Host': 'api-seller.ozon.ru',
                'Client-Id': client_id,
                'Api-Key': auth,
                'Content-Type': 'application/json',}
    
    body ={'sku': [sku]}
    response = requests.post(BASE_URL + url, headers=headers, json=body)
    return response


def answer_feedback(auth, id: str, text: str):
    text  = utils.strip_usage_tail(text)
    url = '/v1/review/comment/create'
    headers = { 'Host': 'api-seller.ozon.ru',
                'Client-Id': client_id,
                'Api-Key': auth,
                'Content-Type': 'application/json',}
    body ={'review_id': id,
           'text': text,
           'mark_review_as_processed': True}
    response = requests.post(BASE_URL + url, headers=headers, json=body)
    print(f'answered {id}')
    return response.status_code


def get_feedback_info(auth, id: str):
    url = '/v1/review/info'
    headers = { 'Host': 'api-seller.ozon.ru',
                'Client-Id': client_id,
                'Api-Key': auth,
                'Content-Type': 'application/json',}
    body ={'review_id': id,}
    response = requests.post(BASE_URL + url, headers=headers, json=body)
    return response