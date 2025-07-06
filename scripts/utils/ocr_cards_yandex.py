import os
import base64
import json
import logging
import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

load_dotenv()
IAM_TOKEN = os.getenv("YANDEX_IAM_TOKEN")
FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")  # если есть, иначе None
assert IAM_TOKEN, "YANDEX_IAM_TOKEN must be set in .env"

CARDS_DIR = "cards_downloaded"
RESULT_FILE = "cards_ocr_texts_yandex.json"

VISION_URL = "https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze"

def extract_text(data):
    # Собирает текст из lines и words на всех уровнях
    lines = []
    try:
        pages = data["results"][0]["results"][0]["textDetection"].get('pages', [])
        for page in pages:
            for block in page.get('blocks', []):
                # Сначала lines
                for line in block.get('lines', []):
                    if 'text' in line:
                        lines.append(line['text'])
                    # Если нет line['text'], собираем из words
                    elif 'words' in line:
                        word_texts = [w['text'] for w in line.get('words', []) if 'text' in w]
                        if word_texts:
                            lines.append(' '.join(word_texts))
                # Если нет lines, собираем из words блока
                if not block.get('lines') and 'words' in block:
                    word_texts = [w['text'] for w in block.get('words', []) if 'text' in w]
                    if word_texts:
                        lines.append(' '.join(word_texts))
    except Exception as e:
        logging.error(f"Ошибка парсинга ответа Vision (words): {e}")
    return "\n".join(lines)

results = {}

for fname in os.listdir(CARDS_DIR):
    if not fname.lower().endswith((".png", ".jpg", ".jpeg")):
        continue
    path = os.path.join(CARDS_DIR, fname)
    with open(path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    req = {
        "analyze_specs": [
            {
                "content": img_b64,
                "features": [{"type": "TEXT_DETECTION", "text_detection_config": {"language_codes": ["ru", "en"]}}]
            }
        ]
    }
    headers = {
        "Authorization": f"Bearer {IAM_TOKEN}",
        "Content-Type": "application/json"
    }
    if FOLDER_ID:
        req["folderId"] = FOLDER_ID
    try:
        resp = requests.post(VISION_URL, headers=headers, json=req, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        text = extract_text(data)
        if not text:
            logging.warning(f"Vision API не вернул текст для {fname}. Сырой ответ: {json.dumps(data, ensure_ascii=False)[:500]}")
        results[fname] = text
        logging.info(f"Yandex OCR: {fname} — {len(text)} символов")
    except Exception as e:
        logging.error(f"Ошибка OCR через Yandex Vision для {fname}: {e}")

with open(RESULT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
logging.info(f"Yandex Vision OCR завершён. Результаты в {RESULT_FILE}") 