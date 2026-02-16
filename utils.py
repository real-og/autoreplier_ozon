from datetime import datetime, timezone


# for cahtGPT
def parse_feedback(feedback_item: dict):
    return {
        "userName": feedback_item.get("userName", ""),
        "rating": feedback_item.get("productValuation"),
        "text": feedback_item.get("text", ""),
        "pros": feedback_item.get("pros", ""),
        "cons": feedback_item.get("cons", ""),
        "productName": (feedback_item.get("productDetails") or {}).get("productName", ""),
        "brandName": (feedback_item.get("productDetails") or {}).get("brandName", ""),
        "bables": feedback_item.get("bables", []),
        "color": feedback_item.get("color", ""),
    }


# from wb to tg
def compose_message(feedback: dict) -> str:
    pd = feedback.get("productDetails") or {}

    fb_id = feedback.get("id", "-")
    user = (feedback.get("userName") or "").strip() or "Без имени"
    rating = feedback.get("productValuation", "-")
    created = feedback.get("createdDate")

    created_str = "—"
    if created:
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00")).astimezone(timezone.utc)
            created_str = dt.strftime("%d.%m.%Y %H:%M UTC")
        except Exception:
            created_str = created

    product_name = pd.get("productName", "—")
    brand = pd.get("brandName", "—")
    supplier_article = pd.get("supplierArticle", "—")
    color = feedback.get("color") or "—"
    subject = feedback.get("subjectName") or pd.get("subjectName") or "—"

    text = (feedback.get("text") or "").strip()
    pros = (feedback.get("pros") or "").strip()
    cons = (feedback.get("cons") or "").strip()

    bables = feedback.get("bables") or []
    tags = ", ".join(bables) if isinstance(bables, list) and bables else "—"

    photos = feedback.get("photoLinks") or []
    photos_count = len(photos) if isinstance(photos, list) else 0

    answer = feedback.get("answer")

    article_for_customer = pd.get('nmId')

    answered = "✅ Есть ответ" if answer else "❌ Нет ответа"

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
        f"Покупатель: <b>{user}</b>",
        f"Фото: <b>{photos_count}</b>", 
        "",
        f"Теги: <b>{tags}</b>",   
        ""   
    ]

    if text:
        parts += [f"Текст: <b>{text}</b>"]
    if pros:
        parts += [f"Плюсы: <b>{pros}</b>"]
    if cons:
        parts += [f"Минусы: <b>{cons}</b>"]

    if not text and not pros and not cons:
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


import re

def strip_usage_tail(text: str) -> str:
    return re.sub(
        r'\n*\s*(?:всего|суммарно)\s+использовано.*$',
        '',
        text,
        flags=re.IGNORECASE | re.DOTALL
    ).rstrip()


def is_valid_proxy(proxy: str) -> bool:
    pattern = re.compile(
        r'^http://'                      # протокол
        r'([a-zA-Z0-9._-]+)'              # логин
        r':'                              
        r'([a-zA-Z0-9._-]+)'              # пароль
        r'@'
        r'('
            r'(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.'  # 1 октет
            r'(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.'  # 2
            r'(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.'  # 3
            r'(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)'    # 4
        r')'
        r':'
        r'([1-9]\d{0,4})$'                # порт
    )

    match = pattern.match(proxy)
    if not match:
        return False