import os
import pytesseract
from PIL import Image
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

CARDS_DIR = "cards_downloaded"
RESULT_FILE = "cards_ocr_texts.json"

results = {}

for fname in os.listdir(CARDS_DIR):
    if not fname.lower().endswith((".png", ".jpg", ".jpeg")):
        continue
    path = os.path.join(CARDS_DIR, fname)
    try:
        img = Image.open(path)
        text = pytesseract.image_to_string(img, lang="rus+eng")
        results[fname] = text
        logging.info(f"OCR: {fname} — {len(text)} символов")
    except Exception as e:
        logging.error(f"Ошибка OCR для {fname}: {e}")

with open(RESULT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
logging.info(f"OCR завершён. Результаты в {RESULT_FILE}") 