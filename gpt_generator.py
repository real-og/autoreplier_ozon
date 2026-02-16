import os
import httpx
from openai import OpenAI
import json
import config_io


http_client = httpx.Client(
    proxy=config_io.get_value('PROXY'),         
    timeout=60.0,
)

client = OpenAI(api_key=config_io.get_value('GPT_KEY'), http_client=http_client)


SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"}
    },
    "required": ["answer"],
    "additionalProperties": False
}


def get_reply(payload: dict | str, recommended = None) -> str:
    if isinstance(payload, dict):
        payload = json.dumps(payload, ensure_ascii=False)

    instructions = config_io.get_value('INSTRUCTIONS')
    if recommended:
        instructions += f" {config_io.get_value('RECOMMEND_INSTRUCTIONS')} {recommended}"

    resp = client.responses.create(
        model="gpt-5-mini",
        instructions=instructions,
        input="Данные отзыва:\n" + payload,
        max_output_tokens=3100,
        text={
            "format": {
                "type": "json_schema",
                "name": "wb_reply",
                "strict": True,
                "schema": SCHEMA
            }
        },
        store=False,  
    )

    raw = resp.output_text

    usage = getattr(resp, "usage", None)
    total_used = None
    if usage:
        total_used = usage.total_tokens
    if not raw or not raw.strip():
        print(resp.model_dump_json(indent=2, ensure_ascii=False))
        raise RuntimeError("Empty output_text (no output_text blocks in response)")
    
    data = json.loads(resp.output_text)
    return data["answer"].strip(), total_used


if __name__ == '__main__':
    print(get_reply('класс'))
    
