import time
import httpx
from openai import OpenAI
import config_io


PROXY_CHECK_URL = 'https://api.ipify.org?format=json'
GPT_CHECK_URL = 'https://api.openai.com/v1/models'
OZON_CHECK_URL = 'https://api-seller.ozon.ru/v1/review/list'


def check_proxy(proxy: str, timeout_s: float = 10.0):
    try:
        with httpx.Client(proxy=proxy, timeout=timeout_s) as client:
            t0 = time.perf_counter()
            r = client.get(PROXY_CHECK_URL)
            r.raise_for_status()
            ip = r.json().get("ip")
            return ip, str(int((time.perf_counter() - t0) * 1000)) + 'ms'
    except Exception:
        return None
    

def check_openai_via_proxy(proxy: str, api_key: str, timeout_s: float = 20.0):
    """
    - (True, status_code)  -> ok
    - (False, status_code) -> 401 - no good openAI token, 403 - ip, 429 - too much requests or no money
    - (False, None)        -> network/proxy problem
    """
    http_client = httpx.Client(proxy=proxy, timeout=timeout_s)
    client = OpenAI(api_key=api_key, http_client=http_client)

    try:
        client.responses.create(
            model="gpt-5-mini",
            input="ping",
            max_output_tokens=16,
            store=False,
        )
        return True, 200

    except Exception as e:
        code = getattr(e, "status_code", None)
        print(e)
        if code is None:
            resp = getattr(e, "response", None)
            code = getattr(resp, "status_code", None)
        return False, code

    finally:
        http_client.close()
    

def check_ozon(ozon_token, timeout_s: float = 10.0):
    client_id = config_io.get_value('CLIENT_ID')
    headers = headers = { 'Host': 'api-seller.ozon.ru',
                'Client-Id': client_id,
                'Api-Key': ozon_token,
                'Content-Type': 'application/json',}
    body ={'status': 'UNPROCESSED',
             'limit': 100,
             'sort_dir': 'DESC'
            }
    try:
        with httpx.Client(timeout=timeout_s) as c:
            r = c.post(OZON_CHECK_URL, headers=headers, json=body)
        return r.is_success, r.status_code
    except httpx.HTTPError as e:
        return False, getattr(getattr(e, "response", None), "status_code", None)

    