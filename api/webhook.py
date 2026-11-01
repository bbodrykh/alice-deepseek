import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")


class handler(BaseHTTPRequestHandler):

  def do_POST(self):
    content_length = int(self.headers.get("Content-Length", 0))
    post_data = self.rfile.read(content_length)
    req = json.loads(post_data.decode("utf-8"))

    # Извлекаем текст, который пользователь сказал Алисе
    user_text = req.get("request", {}).get("command", "").strip()

    # Если фраза пустая (навык только что открылся)
    if not user_text:
      reply_text = (
          "Привет! Я подключена к DeepSeek через Dahl. Задавай любой вопрос,"
          " слушаю."
      )
    else:
      try:
        # Эндпоинт и модель под шлюз Dahl
        url = "https://inference.dahl.global/v1/chat/completions"
        payload = json.dumps({
            "model": "deepseek/deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Отвечай кратко, емко, понятно и живым разговорным"
                        " языком без markdown-разметки (без звездочек и"
                        " решеток), так как твой ответ будет зачитан голосом"
                        " через колонку."
                    ),
                },
                {"role": "user", "content": user_text},
            ],
            "max_tokens": 350,
            "temperature": 0.7,
        }).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        }

        api_req = urllib.request.Request(
            url, data=payload, headers=headers, method="POST"
        )
        with urllib.request.urlopen(api_req, timeout=12) as response:
          res_data = json.loads(response.read().decode("utf-8"))
          reply_text = res_data["choices"][0]["message"]["content"]

      except Exception as e:
        reply_text = "Произошла ошибка при обращении к нейросети. Попробуй повторить вопрос."

    # Формируем стандартный ответ для протокола Яндекс Диалогов
    response_payload = {
        "response": {"text": reply_text, "end_session": False},
        "version": "1.0",
    }

    self.send_response(200)
    self.send_header("Content-Type", "application/json; charset=utf-8")
    self.end_headers()
    self.wfile.write(json.dumps(response_payload).encode("utf-8"))

  def do_GET(self):
    # Ответ на случайную проверку доступности через браузер
    self.send_response(200)
    self.send_header("Content-Type", "text/plain; charset=utf-8")
    self.end_headers()
    self.wfile.write("Webhook is active".encode("utf-8"))
