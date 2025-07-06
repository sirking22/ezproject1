import os
import yadisk
import logging
from dotenv import load_dotenv

# Логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Загрузка переменных окружения
load_dotenv()
YA_TOKEN = os.getenv("YA_ACCESS_TOKEN") or os.getenv("YANDEX_TOKEN")
assert YA_TOKEN, "YA_ACCESS_TOKEN or YANDEX_TOKEN must be set in .env"

y = yadisk.YaDisk(token=YA_TOKEN)

LOCAL_DIR = "cards_downloaded"
os.makedirs(LOCAL_DIR, exist_ok=True)

# Поиск папки по имени
FOLDER_NAME = "Проверка карточек"
def find_folder_path(folder_name):
    for item in y.listdir("/"):
        if item['type'] == 'dir' and item['name'] == folder_name:
            return item['path']
    raise FileNotFoundError(f"Папка '{folder_name}' не найдена на Яндекс.Диске")

folder_path = find_folder_path(FOLDER_NAME)
logging.info(f"Папка найдена: {folder_path}")

# Получаем список файлов
files = [f for f in y.listdir(folder_path) if f['type'] == 'file' and f['name'].lower().endswith(('.png', '.jpg', '.jpeg'))]
logging.info(f"Найдено файлов: {len(files)}")

for f in files:
    local_path = os.path.join(LOCAL_DIR, f['name'])
    if os.path.exists(local_path):
        logging.info(f"Файл уже скачан: {f['name']}")
        continue
    try:
        y.download(f["path"], local_path)
        logging.info(f"Скачан: {f['name']}")
    except Exception as e:
        logging.error(f"Ошибка при скачивании {f['name']}: {e}") 