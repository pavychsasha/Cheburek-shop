from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


PHRASES_EN_TO_UK = {
    "Cheburek with meat": "Чебурек з м'ясом",
    "Cheburek with cheese": "Чебурек з сиром",
    "Cheburek with meat and cheese": "Чебурек з м'ясом та сиром",
    "Cheburek with chicken": "Чебурек з куркою",
    "Cheburek with chicken and cheese": "Чебурек з куркою та сиром",
    "Cheburek with chicken, cheese, and mushrooms": (
        "Чебурек з куркою, сиром та грибами"
    ),
    "Pie with potatoes": "Пиріжок з картоплею",
    "Pie with cabbage": "Пиріжок з капустою",
    "Pie with cheese and herbs": "Пиріжок з сиром та зеленню",
    "Coca-Cola 0.5L": "Coca-Cola 0.5 л",
    "Sprite 0.5L": "Sprite 0.5 л",
    "French fries": "Картопля фрі",
    "Nuggets": "Нагетси",
}

WORDS_EN_TO_UK = {
    "cheburek": "чебурек",
    "chebureks": "чебуреки",
    "pie": "пиріжок",
    "pies": "пиріжки",
    "with": "з",
    "meat": "м'ясом",
    "cheese": "сиром",
    "chicken": "куркою",
    "mushrooms": "грибами",
    "potatoes": "картоплею",
    "cabbage": "капустою",
    "herbs": "зеленню",
    "fried": "смажений",
    "baked": "печений",
    "fresh": "свіжий",
    "hot": "гарячий",
    "cold": "холодний",
    "drink": "напій",
    "drinks": "напої",
    "snack": "закуска",
    "snacks": "закуски",
    "and": "та",
    "for": "для",
    "local": "локальний",
    "delivery": "доставка",
    "crispy": "хрусткий",
    "juicy": "соковитий",
    "classic": "класичний",
    "signature": "фірмовий",
    "sauce": "соус",
    "portion": "порція",
    "served": "подається",
    "freshly": "свіжо",
    "made": "приготований",
}


def normalize_language(language: str) -> str:
    language = (language or "").strip().lower()
    return {"ukr": "uk", "ua": "uk", "eng": "en"}.get(language, language)


def translate_token(token: str) -> str:
    leading = token[: len(token) - len(token.lstrip(".,!?;:()[]{}\"'"))]
    trailing = token[len(token.rstrip(".,!?;:()[]{}\"'")) :]
    core = token[len(leading) : len(token) - len(trailing) if trailing else len(token)]
    if not core:
        return token

    translated = WORDS_EN_TO_UK.get(core.lower(), core)
    if core[:1].isupper():
        translated = translated[:1].upper() + translated[1:]
    return f"{leading}{translated}{trailing}"


def translate_text(text: str, source: str, target: str) -> str:
    source = normalize_language(source)
    target = normalize_language(target)
    if not text or source == target:
        return text
    if source != "en" or target != "uk":
        return text
    if text in PHRASES_EN_TO_UK:
        return PHRASES_EN_TO_UK[text]
    return " ".join(translate_token(token) for token in text.split(" "))


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        if self.path == "/languages":
            self._send_json(
                200,
                [
                    {"code": "en", "name": "English"},
                    {"code": "uk", "name": "Ukrainian"},
                ],
            )
            return
        self._send_json(404, {"detail": "Not found"})

    def do_POST(self) -> None:
        if self.path != "/translate":
            self._send_json(404, {"detail": "Not found"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(400, {"detail": "Invalid JSON"})
            return

        text = str(payload.get("q", ""))
        source = str(payload.get("source", "en"))
        target = str(payload.get("target", "uk"))
        self._send_json(
            200,
            {
                "translatedText": translate_text(text, source, target),
            },
        )

    def log_message(self, fmt: str, *args: object) -> None:
        return


def main() -> None:
    host = os.environ.get("TRANSLATOR_HOST", "0.0.0.0")
    port = int(os.environ.get("TRANSLATOR_PORT", "5000"))
    server = ThreadingHTTPServer((host, port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
