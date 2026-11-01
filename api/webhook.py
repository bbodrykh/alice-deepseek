import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")


class handler(BaseHTTPRequestHandler):

  def do_POST(self):
    content_length = int(self.headers["Content-Length"])
    post_data = self.rfile.read(content_length)
    req = json.loads(post_data.decode("utf-8"))

    user_text = req.get("request", {}).get("command", "").strip()
    session = req.get("session", {})

    if not user_text:
      reply_text = (
          "Привет! Я подключена к DeepSeek. Задавай любой вопрос, слушаю."
      )
    else:
      try:
        url = "https://api.deepseek.com/chat/completions"
        payload = json.dumps({
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Отвечай кратко, емко и разговорным языком, так как твой"
                        " ответ будет озвучен голосом."
                    ),
                },
                {"role": "user", "content": user_text},
            ],
            "max_tokens": 300,
        }).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        }

        api_req = urllib.request.Request(
            url, data=payload, headers=headers, method="POST"
        )
        with urllib.request.urlopen(api_req, timeout=10) as response:
          res_data = json.loads(response.read().decode("utf-8"))
          reply_text = res_data["choices"][0]["message"]["content"]
      except Exception:
        reply_text = "Ошибка при обращении к нейросети. Попробуй еще раз."

    response = {
        "response": {"text": reply_text, "end_session": False},
        "version": "1.0",
    }

    self.send_response(200)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(json.dumps(response).encode("utf-8"))
