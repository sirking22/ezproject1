import json
import os
import requests
import logging
import base64
import tempfile
import subprocess
from flask import Flask, request

logging.basicConfig(level=logging.INFO)
logging.info("=== ФУНКЦИЯ ЗАПУЩЕНА ===")

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
IAM_TOKEN = os.environ.get("YANDEX_IAM_TOKEN")
FOLDER_ID = os.environ.get("YANDEX_FOLDER_ID")

app = Flask(__name__)

@app.route("/", methods=["POST"])
def main():
    event = request.get_json(force=True)
    return handler(event, {})

def recognize_audio(file_path):
    with open(file_path, "rb") as f:
        audio_bytes = f.read()
    headers = {
        "Authorization": f"Bearer {IAM_TOKEN}",
        "Content-Type": "audio/ogg"
    }
    params = {
        "folderId": FOLDER_ID,
        "lang": "ru-RU",
        "enableAutomaticPunctuation": "true"
    }
    response = requests.post(
        "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
        headers=headers,
        params=params,
        data=audio_bytes,
    )
    logging.info(f"SpeechKit response: {response.text}")
    result = response.json()
    return result.get("result")


def ogg_to_wav(ogg_path):
    wav_path = tempfile.mktemp(suffix=".wav")
    subprocess.run([
        "ffmpeg", "-y", "-i", ogg_path,
        "-ar", "16000", "-ac", "1",
        "-f", "wav", "-acodec", "pcm_s16le",
        wav_path
    ], check=True)
    return wav_path


def handler(event, context):
    logging.info(f"EVENT: {json.dumps(event)}")
    try:
        message = event.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")

        # === Обработка голосовых сообщений ===
        if "voice" in message:
            file_id = message["voice"]["file_id"]
            resp = requests.get(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile",
                params={"file_id": file_id}
            )
            file_path = resp.json()["result"]["file_path"]
            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
            ogg_data = requests.get(file_url).content

            with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as ogg_file:
                ogg_file.write(ogg_data)
                ogg_path = ogg_file.name
            recognized = recognize_audio(ogg_path)

            reply = f"Распознано: {recognized}" if recognized else "Ошибка распознавания"
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": reply}
            )
        elif TELEGRAM_TOKEN and chat_id and text:
            reply = f"Вы написали: {text}"
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": reply}
            )
        elif not TELEGRAM_TOKEN:
            logging.error("TELEGRAM_BOT_TOKEN не найден!")

        return {
            "statusCode": 200,
            "body": json.dumps({"ok": True})
        }
    except Exception as e:
        logging.error(f"ERROR: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"ok": False, "error": str(e)})
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port) 