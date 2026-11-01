import os
import json
import urllib.request

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()

def handler(request):
    # 1. Чтение входящих данных от Яндекс Диалогов
    try:
        if hasattr(request, "get_json"):
            req = request.get_json() or {}
        elif hasattr(request, "body"):
            req = json.loads(request.body.decode("utf-8")) if isinstance(request.body, bytes) else json.loads(request.body)
        else:
            req = json.loads(request)
    except Exception:
        req = {}

    user_text = req.get("request", {}).get("command", "").strip()
    session = req.get("session", {})

    # 2. Обработка запроса
    if not user_text:
        reply_text = "Привет! Я подключена к DeepSeek через Dahl. Задавай любой вопрос, слушаю."
    else:
        try:
            url = "https://inference.dahl.global/v1/chat/completions"
            payload = json.dumps({
                "model": "deepseek-ai/DeepSeek-V4-Flash-0731",
                "messages": [
                    {
                        "role": "system",
                        "content": "Отвечай кратко, емко, понятно и разговорным языком без markdown-разметки (без звездочек и решеток), так как твой ответ будет озвучен вслух."
                    },
                    {"role": "user", "content": user_text}
                ],
                "max_tokens": 350,
                "temperature": 0.7
            }).encode("utf-8")

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            }

            api_req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(api_req, timeout=12) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                reply_text = res_data["choices"][0]["message"]["content"]
        except Exception:
            reply_text = "Ошибка при обращении к нейросети. Проверьте баланс или ключ Dahl."

    # 3. Формирование ответа в строгом формате Яндекс Диалогов
    response_body = {
        "response": {
            "text": reply_text,
            "end_session": False
        },
        "session": {
            "session_id": session.get("session_id", ""),
            "message_id": session.get("message_id", 0),
            "user_id": session.get("user_id", "")
        },
        "version": "1.0"
    }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json; charset=utf-8"
        },
        "body": json.dumps(response_body, ensure_ascii=False)
    }
