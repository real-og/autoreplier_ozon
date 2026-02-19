from datetime import datetime, timezone, timedelta
import re


#for gpt
def parse_feedback(feedback_item: dict, product_info: dict):
    return {
        "rating": feedback_item.get("rating"),
        "text": feedback_item.get("text", ""),
        "productName": product_info.get('name', ""),
    }


# from wb to tg
def compose_message(feedback: dict, product_info: dict) -> str:
    fb_id = feedback.get("id", "-")
    rating = feedback.get("rating", "-")
    created = feedback.get("published_at")
    created_str = "—"
    if created:
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00")).astimezone(timezone.utc)
            created_str = dt.strftime("%d.%m.%Y %H:%M UTC")
        except Exception:
            created_str = created

    product_name = product_info.get("name", "—")
    supplier_article = product_info.get("offer_id", "—")
    text = (feedback.get("text") or "").strip()
    photos_count = feedback.get("photos_amount", '0')
    article_for_customer = feedback.get('sku')

    if int(rating) == 5:
        symbol_for_rate = '✅'
    elif int(rating) > 2:
        symbol_for_rate = '⚠️'
    else:
        symbol_for_rate = '💀'

    parts = [ 
        f"Оценка: <b>{rating}</b>{symbol_for_rate}", 
        "",
        f"Время: <b>{created_str}</b>",
        "",
        f"Товар: <b>{product_name}</b>",
        "",
        f"Артикул продавца: <b>{supplier_article}</b>",
        f"Карточка: <b>{article_for_customer}</b>",
        "",
        f"Фото: <b>{photos_count}</b>", 
        "",
    ]

    if text:
        parts += [f"Текст: <b>{text}</b>"]

    if not text:
        parts += ["Отзыв без текста"]

    parts += ["", f"ID: <i>{fb_id}</i>"]
    return "\n".join(parts)


# the last symbols with prefix ...
def short_tail(s: str, tail: int = 6) -> str:
    if s is None:
        return ""
    s = str(s)
    if len(s) <= tail:
        return s
    return "..." + s[-tail:]


def strip_usage_tail(text: str) -> str:
    return re.sub(
        r'\n*\s*(?:всего|суммарно)\s+использовано.*$',
        '',
        text,
        flags=re.IGNORECASE | re.DOTALL
    ).rstrip()


def is_valid_proxy(proxy: str) -> bool:
    pattern = re.compile(
        r'^http://'                     
        r'([a-zA-Z0-9._-]+)'              
        r':'                              
        r'([a-zA-Z0-9._-]+)'             
        r'@'
        r'('
            r'(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.'  
            r'(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.'  
            r'(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.'  
            r'(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)'    
        r')'
        r':'
        r'([1-9]\d{0,4})$'                
    )

    match = pattern.match(proxy)
    if not match:
        return False
    

def is_fresher_than_days(ts: str, days: int = 30) -> bool:

    if not isinstance(ts, str) or not ts:
        return False

    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

    except ValueError:
        return False

    now = datetime.now(timezone.utc)
    return (now - dt) < timedelta(days=days)