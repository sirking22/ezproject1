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


class YandexDiskUploader:
    """Загрузчик файлов на Яндекс.Диск"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://cloud-api.yandex.net/v1/disk"
        
    def upload_file(self, file_path: str, remote_path: str) -> bool:
        """Загружает файл на Яндекс.Диск"""
        # TODO: Реализовать загрузку файла
        print(f"YandexDiskUploader: Загрузка {file_path} -> {remote_path}")
        return True
        
    def get_upload_url(self, remote_path: str) -> Optional[str]:
        """Получает URL для загрузки файла"""
        # TODO: Реализовать получение URL
        return f"https://test-upload-url.yandex.net/{remote_path}"
        
    def get_public_url(self, remote_path: str) -> Optional[str]:
        """Получает публичную ссылку на файл"""
        # TODO: Реализовать получение публичной ссылки
        return f"https://disk.yandex.ru/i/{remote_path}" 