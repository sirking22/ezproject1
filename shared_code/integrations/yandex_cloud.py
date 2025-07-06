import os
from typing import Optional

class YandexCloudClient:
    """Универсальный клиент для Яндекс Облака. Настройки берутся из env вызывающего проекта."""
    def __init__(self):
        self.api_key = os.getenv("YANDEX_CLOUD_API_KEY")
        self.folder_id = os.getenv("YANDEX_CLOUD_FOLDER_ID")
        self.endpoint = os.getenv("YANDEX_CLOUD_ENDPOINT", "https://api.yandexcloud.net")
        if not self.api_key or not self.folder_id:
            raise ValueError("YANDEX_CLOUD_API_KEY и YANDEX_CLOUD_FOLDER_ID должны быть заданы в env")

    def do_something(self):
        # TODO: реализовать вызовы к Яндекс Облаку
        pass 