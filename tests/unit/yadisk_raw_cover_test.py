import requests
import os

YANDEX_TOKEN = os.getenv("YANDEX_TOKEN")
FOLDER = "/TelegramImport_20250621_025209/group_20240125_031952"
headers = {"Authorization": f"OAuth {YANDEX_TOKEN}"}

# Получить список файлов в папке
list_url = "https://cloud-api.yandex.net/v1/disk/resources"
params = {"path": FOLDER, "limit": 1000}
resp = requests.get(list_url, params=params, headers=headers)
data = resp.json()

print("DEBUG API RESPONSE:", data)

items = data.get("_embedded", {}).get("items", [])
print(f"Найдено файлов: {len(items)}")

for item in items:
    path = item["path"]
    name = item["name"]
    if not name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        continue
    print(f"\nФайл: {name}")
    # Получить public_url
    meta = requests.get(list_url, params={"path": path}, headers=headers).json()
    public_url = meta.get("public_url")
    if not public_url:
        # Сделать публичным
        publish_url = "https://cloud-api.yandex.net/v1/disk/resources/publish"
        requests.put(publish_url, params={"path": path}, headers=headers)
        meta = requests.get(list_url, params={"path": path}, headers=headers).json()
        public_url = meta.get("public_url")
    if public_url:
        # Получить RAW-ссылку
        download_url = "https://cloud-api.yandex.net/v1/disk/resources/download"
        resp = requests.get(download_url, params={"public_key": public_url})
        raw_url = resp.json().get("href")
        print("RAW ссылка для Notion:", raw_url)
    else:
        print("Не удалось получить public_url!") 