import os
import asyncio
import re
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv
from notion_client import AsyncClient
import yadisk

load_dotenv()

class MediaCoverManager:
    def __init__(self):
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.ideas_db_id = os.getenv("IDEAS_DB", "ad92a6e2-1485-428c-84de-8587706b3be1")
        self.yadisk_token = os.getenv("YANDEX_DISK_TOKEN")
        self.figma_token = os.getenv("FIGMA_TOKEN")  # Добавляем Figma токен
        if not self.notion_token:
            raise RuntimeError("NOTION_TOKEN не найден в env")
        if not self.yadisk_token:
            raise RuntimeError("YANDEX_DISK_TOKEN не найден в env")
        self.notion = AsyncClient(auth=str(self.notion_token))
        self.yadisk = yadisk.YaDisk(token=str(self.yadisk_token))

    def extract_figma_info(self, figma_url: str) -> Optional[Dict[str, Optional[str]]]:
        """
        Извлекает file_key и node_id из Figma ссылки
        Поддерживает форматы:
        - https://www.figma.com/file/FILE_KEY/...
        - https://www.figma.com/proto/FILE_KEY/...
        - https://www.figma.com/design/FILE_KEY/...
        """
        patterns = [
            r'figma\.com/file/([a-zA-Z0-9]+)',
            r'figma\.com/proto/([a-zA-Z0-9]+)',
            r'figma\.com/design/([a-zA-Z0-9]+)'
        ]

        file_key = None
        for pattern in patterns:
            match = re.search(pattern, figma_url)
            if match:
                file_key = match.group(1)
                break

        if not file_key:
            return None

        # Исправлено: node_id может содержать дефисы и цифры
        node_match = re.search(r'node-id=([a-zA-Z0-9\-]+)', figma_url)
        node_id = node_match.group(1) if node_match else None
        if node_id:
            node_id = node_id.replace('-', ':')

        return {
            'file_key': file_key,
            'node_id': node_id
        }

    def get_figma_image_url(self, file_key: str, node_id: Optional[str] = None,
                           format: str = "png", scale: int = 2) -> Optional[str]:
        """
        Получает URL изображения из Figma API
        """
        if not self.figma_token:
            print("⚠️ FIGMA_TOKEN не найден в env")
            return None

        try:
            # Формируем URL для экспорта
            if node_id:
                url = f"https://api.figma.com/v1/images/{file_key}?ids={node_id}&format={format}&scale={scale}"
            else:
                # Если нет node_id, экспортируем весь файл
                url = f"https://api.figma.com/v1/images/{file_key}?format={format}&scale={scale}"

            headers = {
                'X-Figma-Token': self.figma_token
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()

            if node_id:
                # Для конкретного узла
                if 'images' in data and node_id in data['images']:
                    return data['images'][node_id]
            else:
                # Для всего файла - берем первый доступный узел
                if 'images' in data and data['images']:
                    return list(data['images'].values())[0]

            print(f"❌ Не удалось получить изображение из Figma API")
            return None

        except Exception as e:
            print(f"❌ Ошибка получения изображения из Figma: {e}")
            return None

    async def apply_figma_cover(self, notion_page_id: str, figma_url: str) -> bool:
        """
        Устанавливает обложку Notion из Figma ссылки
        """
        print(f"🎨 Применяю Figma cover для {notion_page_id}")

        # Извлекаем информацию из Figma ссылки
        figma_info = self.extract_figma_info(figma_url)
        if not figma_info:
            print(f"❌ Не удалось извлечь информацию из Figma ссылки: {figma_url}")
            return False

        # Получаем URL изображения из Figma
        image_url = self.get_figma_image_url(
            file_key=figma_info['file_key'],
            node_id=figma_info['node_id']
        )

        if not image_url:
            print(f"❌ Не удалось получить изображение из Figma")
            return False

        try:
            # Устанавливаем cover в Notion
            await self.notion.pages.update(
                page_id=notion_page_id,
                cover={
                    "type": "external",
                    "external": {"url": image_url}
                }
            )
            print(f"✅ Figma cover применен для {notion_page_id}: {image_url}")
            return True
        except Exception as e:
            print(f"❌ Ошибка применения Figma cover для {notion_page_id}: {e}")
            return False

    async def batch_apply_figma_covers(self, limit: int = 20):
        """
        Массово применяет Figma covers для записей с Figma ссылками
        """
        resp = await self.notion.databases.query(
            database_id=str(self.ideas_db_id),
            page_size=limit,
            sorts=[{"property": "Created time", "direction": "descending"}]
        )

        applied = 0
        for idea in resp.get('results', []):
            props = idea.get('properties', {})
            # Проверяем поле URL
            url_field = props.get('URL', {})
            url = url_field.get('url', '') if url_field else ''

            # Проверяем поле Файлы
            files_field = props.get('Файлы', {})
            files_url = files_field.get('url', '') if files_field else ''

            # Ищем Figma ссылки
            figma_url = None
            if 'figma.com' in url:
                figma_url = url
            elif 'figma.com' in files_url:
                figma_url = files_url

            if not figma_url:
                continue

            print(f"\n=== Обработка карточки {idea['id']} с Figma ссылкой ===")
            success = await self.apply_figma_cover(idea['id'], figma_url)
            if success:
                applied += 1

        print(f"\nИтого применено Figma covers: {applied}/{len(resp.get('results', []))}")

    async def apply_cover_from_url(self, notion_page_id: str, url: str) -> bool:
        """
        Универсальный метод для установки cover из различных источников
        """
        if 'figma.com' in url:
            return await self.apply_figma_cover(notion_page_id, url)
        elif 'yadi.sk' in url or 'disk.yandex.ru' in url:
            # Для Яндекс.Диска используем существующий метод
            return await self.apply_cover_from_yadisk_url(notion_page_id, url)
        else:
            print(f"⚠️ Неподдерживаемый URL для cover: {url}")
            return False

    async def apply_cover_from_yadisk_url(self, notion_page_id: str, yadisk_url: str) -> bool:
        """
        Устанавливает cover из публичной ссылки Яндекс.Диска
        """
        try:
            meta = self.yadisk.get_meta(yadisk_url)
            if getattr(meta, 'type', None) != 'file':
                print(f"❌ Ссылка не на файл: {yadisk_url}")
                return False

            preview_url = getattr(meta, 'preview', None) or getattr(meta, 'public_url', None)
            if not preview_url:
                print(f"❌ Нет preview/public_url для {yadisk_url}")
                return False

            await self.notion.pages.update(
                page_id=notion_page_id,
                cover={
                    "type": "external",
                    "external": {"url": preview_url}
                }
            )
            print(f"✅ Yandex.Disk cover применен для {notion_page_id}: {preview_url}")
            return True
        except Exception as e:
            print(f"❌ Ошибка применения Yandex.Disk cover для {notion_page_id}: {e}")
            return False

    async def get_ideas_with_yadisk(self, limit=100) -> List[Dict]:
        resp = await self.notion.databases.query(
            database_id=str(self.ideas_db_id),
            page_size=limit,
            sorts=[{"property": "Created time", "direction": "descending"}]
        )
        ideas = []
        for idea in resp.get('results', []):
            props = idea.get('properties', {})
            url = props.get('URL', {}).get('url', '') or ''
            files_url = props.get('Файлы', {}).get('url', '') or ''
            if 'yadi.sk' in url or 'yadi.sk' in files_url:
                ideas.append({
                    'id': idea['id'],
                    'url': url,
                    'files_url': files_url,
                    'cover': idea.get('cover'),
                    'title': self._extract_title(props.get('Name', {}))
                })
        return ideas

    def get_preview_url(self, public_url: str) -> str:
        try:
            meta = self.yadisk.get_meta(public_url)
            preview = getattr(meta, 'preview', None)
            if isinstance(preview, str):
                return preview if preview else ''
        except Exception as e:
            print(f"   ⚠️ Не удалось получить preview для {public_url}: {e}")
        return ''

    def get_direct_image_url(self, yadisk_path: str) -> str:
        """
        Получает прямую ссылку на изображение с Яндекс.Диска
        Сначала публикует файл, затем получает прямую ссылку
        """
        try:
            print(f"🔗 Получаю прямую ссылку для {yadisk_path}")
            
            # Проверяем, опубликован ли файл
            if not self.is_published(yadisk_path):
                print(f"🌍 Публикую файл: {yadisk_path}")
                self.yadisk.publish(yadisk_path)
            
            # Получаем метаданные
            meta = self.yadisk.get_meta(yadisk_path)
            public_url = getattr(meta, 'public_url', None)
            
            if not public_url:
                print(f"❌ Нет public_url для {yadisk_path}")
                return ''
            
            # Для получения прямой ссылки на изображение используем специальный формат
            # Яндекс.Диск предоставляет прямые ссылки через /i/ в URL
            if public_url.startswith('https://yadi.sk/d/'):
                # Извлекаем ID файла из public_url
                file_id = public_url.split('/')[-1]
                direct_url = f"https://yadi.sk/i/{file_id}"
                print(f"✅ Прямая ссылка: {direct_url}")
                return direct_url
            elif public_url.startswith('https://disk.yandex.ru/d/'):
                # Для нового формата URL
                file_id = public_url.split('/')[-1]
                direct_url = f"https://disk.yandex.ru/i/{file_id}"
                print(f"✅ Прямая ссылка: {direct_url}")
                return direct_url
            elif public_url.startswith('https://yadi.sk/i/'):
                # Уже прямая ссылка
                print(f"✅ Уже прямая ссылка: {public_url}")
                return public_url
            elif public_url.startswith('https://disk.yandex.ru/i/'):
                # Уже прямая ссылка
                print(f"✅ Уже прямая ссылка: {public_url}")
                return public_url
            else:
                print(f"⚠️ Неизвестный формат public_url: {public_url}")
                return public_url
                
        except Exception as e:
            print(f"❌ Ошибка получения прямой ссылки для {yadisk_path}: {e}")
            return ''

    def get_public_image_url(self, yadisk_path: str) -> str:
        """
        Получает действительно публичную ссылку на изображение
        которая открывается для всех пользователей без авторизации
        """
        try:
            print(f"🌍 Получаю публичную ссылку для {yadisk_path}")
            
            # Проверяем, опубликован ли файл
            if not self.is_published(yadisk_path):
                print(f"🌍 Публикую файл: {yadisk_path}")
                self.yadisk.publish(yadisk_path)
            
            # Получаем метаданные
            meta = self.yadisk.get_meta(yadisk_path)
            public_url = getattr(meta, 'public_url', None)
            
            if not public_url:
                print(f"❌ Нет public_url для {yadisk_path}")
                return ''
            
            # Пробуем получить preview URL (это может быть прямая ссылка на изображение)
            preview_url = getattr(meta, 'preview', None)
            if preview_url and isinstance(preview_url, str):
                print(f"✅ Найден preview URL: {preview_url}")
                return preview_url
            
            # Если preview нет, пробуем создать прямую ссылку
            if public_url.startswith('https://yadi.sk/d/'):
                file_id = public_url.split('/')[-1]
                # Пробуем разные форматы публичных ссылок
                possible_urls = [
                    f"https://yadi.sk/i/{file_id}",
                    f"https://yadi.sk/d/{file_id}",
                    f"https://disk.yandex.ru/i/{file_id}",
                    f"https://disk.yandex.ru/d/{file_id}"
                ]
                
                # Проверяем каждый URL на доступность
                import requests
                for url in possible_urls:
                    try:
                        response = requests.head(url, timeout=5)
                        if response.status_code == 200:
                            print(f"✅ Найдена рабочая публичная ссылка: {url}")
                            return url
                    except:
                        continue
                
                # Если ничего не работает, возвращаем исходную ссылку
                print(f"⚠️ Не удалось проверить доступность, возвращаю: {public_url}")
                return public_url
                
            elif public_url.startswith('https://disk.yandex.ru/d/'):
                file_id = public_url.split('/')[-1]
                # Аналогично для нового формата
                possible_urls = [
                    f"https://disk.yandex.ru/i/{file_id}",
                    f"https://disk.yandex.ru/d/{file_id}",
                    f"https://yadi.sk/i/{file_id}",
                    f"https://yadi.sk/d/{file_id}"
                ]
                
                import requests
                for url in possible_urls:
                    try:
                        response = requests.head(url, timeout=5)
                        if response.status_code == 200:
                            print(f"✅ Найдена рабочая публичная ссылка: {url}")
                            return url
                    except:
                        continue
                
                print(f"⚠️ Не удалось проверить доступность, возвращаю: {public_url}")
                return public_url
                
            else:
                print(f"⚠️ Неизвестный формат public_url: {public_url}")
                return public_url
                
        except Exception as e:
            print(f"❌ Ошибка получения публичной ссылки для {yadisk_path}: {e}")
            return ''

    async def apply_covers(self, ideas: List[Dict]):
        applied = 0
        for idea in ideas:
            public_url = idea['url'] if 'yadi.sk' in idea['url'] else idea['files_url']
            preview_url = self.get_preview_url(public_url)
            if not preview_url:
                print(f"❌ Нет preview для {public_url}")
                continue
            try:
                await self.notion.pages.update(
                    page_id=idea['id'],
                    cover={
                        "type": "external",
                        "external": {"url": preview_url}
                    }
                )
                print(f"✅ Обложка применена: {idea['title'][:40]}... -> {preview_url}")
                applied += 1
            except Exception as e:
                print(f"❌ Ошибка применения cover для {idea['title']}: {e}")
        print(f"\nИтого применено: {applied}/{len(ideas)}")

    def _extract_title(self, prop: dict) -> str:
        # Вытаскивает plain_text из поля типа title/rich_text
        if not prop:
            return ''
        if prop.get('type') == 'title' and prop.get('title') and isinstance(prop['title'], list) and len(prop['title']) > 0:
            pt = prop['title'][0].get('plain_text', '')
            if pt is None:
                return ''
            return str(pt)
        if prop.get('type') == 'rich_text' and prop.get('rich_text') and isinstance(prop['rich_text'], list) and len(prop['rich_text']) > 0:
            pt = prop['rich_text'][0].get('plain_text', '')
            if pt is None:
                return ''
            return str(pt)
        return ''

    def is_published(self, yadisk_path: str) -> bool:
        try:
            meta = self.yadisk.get_meta(yadisk_path)
            return bool(getattr(meta, 'public_url', None))
        except Exception:
            return False

    def find_yadisk_path_by_name(self, filename: str, start_folder: str = "/") -> str:
        start_folder = str(start_folder or "/")
        print(f"🔍 Ищу файл {filename} в {start_folder}")
        try:
            for item in self.yadisk.listdir(start_folder):
                if item.type == "file" and item.name == filename:
                    print(f"✅ Найден файл: {item.path}")
                    return item.path
                elif item.type == "dir":
                    found = self.find_yadisk_path_by_name(filename, str(item.path or "/"))
                    if found:
                        return found
        except Exception as e:
            print(f"Ошибка обхода {start_folder}: {e}")
        return ""

    def publish_and_get_preview(self, yadisk_path: str) -> str:
        print(f"⏩ Публикую и получаю публичную ссылку для {yadisk_path}")
        try:
            # Используем новый метод для получения публичной ссылки
            public_url = self.get_public_image_url(yadisk_path)
            if public_url:
                print(f"✅ Получена публичная ссылка: {public_url}")
                return public_url
            else:
                print(f"❌ Не удалось получить публичную ссылку для {yadisk_path}")
                return ''
        except Exception as e:
            print(f"⚠️ Не удалось получить публичную ссылку для {yadisk_path}: {e}")
            return ''

    async def apply_cover_from_yadisk_path(self, notion_page_id: str, yadisk_path: str):
        preview_url = self.publish_and_get_preview(yadisk_path)
        if not preview_url:
            print(f"❌ Нет preview/public_url для {yadisk_path}")
            return False
        try:
            print(f"➡️ Ставлю обложку для {notion_page_id}: {preview_url}")
            await self.notion.pages.update(
                page_id=notion_page_id,
                cover={
                    "type": "external",
                    "external": {"url": preview_url}
                }
            )
            print(f"✅ Обложка применена для {notion_page_id}: {preview_url}")
            return True
        except Exception as e:
            print(f"❌ Ошибка применения cover для {notion_page_id}: {e}")
            return False

    async def batch_apply_covers_from_paths(self, limit=50):
        # Ищет карточки с путём к файлу Яндекс.Диска в поле 'Файлы' (или др.)
        resp = await self.notion.databases.query(
            database_id=str(self.ideas_db_id),
            page_size=limit,
            sorts=[{"property": "Created time", "direction": "descending"}]
        )
        applied = 0
        for idea in resp.get('results', []):
            props = idea.get('properties', {})
            yadisk_path = props.get('Файлы', {}).get('rich_text', [{}])[0].get('plain_text', '')
            if not yadisk_path or not yadisk_path.startswith('/'):
                continue
            ok = await self.apply_cover_from_yadisk_path(idea['id'], yadisk_path)
            if ok:
                applied += 1
        print(f"\nИтого применено обложек по путям: {applied}/{len(resp.get('results', []))}")

    async def apply_cover_by_filename(self, notion_page_id: str, filename: str):
        yadisk_path = self.find_yadisk_path_by_name(filename)
        if not yadisk_path:
            print(f"❌ Файл {filename} не найден на Яндекс.Диске")
            return False
        return await self.apply_cover_from_yadisk_path(notion_page_id, yadisk_path)

    async def batch_apply_covers_by_filename(self, limit=50):
        resp = await self.notion.databases.query(
            database_id=str(self.ideas_db_id),
            page_size=limit,
            sorts=[{"property": "Created time", "direction": "descending"}]
        )
        applied = 0
        for idea in resp.get('results', []):
            props = idea.get('properties', {})
            name_field = self._extract_title(props.get('Name', {}))
            if name_field and any(ext in name_field for ext in ['.jpg', '.jpeg', '.png']):
                filename = name_field.strip()
                print(f"\n=== Обработка карточки {idea['id']} с файлом {filename} ===")
                ok = await self.apply_cover_by_filename(idea['id'], filename)
                if ok:
                    applied += 1
        print(f"\nИтого применено обложек по имени файла: {applied}/{len(resp.get('results', []))}")

    def get_first_jpeg_in_yadisk_folder(self, folder_url: str) -> str:
        # Получает путь к папке по публичной ссылке, возвращает путь первого jpeg-файла
        try:
            meta = self.yadisk.get_meta(folder_url)
            if getattr(meta, 'type', None) == 'dir':
                folder_path = getattr(meta, 'path', None)
                if not folder_path:
                    return ""
                for item in self.yadisk.listdir(folder_path):
                    name = str(getattr(item, 'name', '') or "")
                    if getattr(item, 'type', None) == "file" and name.lower().endswith(('.jpg', '.jpeg', '.png')):
                        print(f"✅ Первый jpeg в папке {folder_path}: {getattr(item, 'path', '')}")
                        return str(getattr(item, 'path', '') or "")
        except Exception as e:
            print(f"Ошибка получения jpeg из папки по ссылке {folder_url}: {e}")
        return ""

    async def batch_apply_yadisk_jpeg_to_file_field(self, limit=20):
        resp = await self.notion.databases.query(
            database_id=str(self.ideas_db_id),
            page_size=limit,
            sorts=[{"property": "Created time", "direction": "descending"}]
        )
        applied = 0
        for idea in resp.get('results', []):
            props = idea.get('properties', {})
            file_url = self._extract_url(props.get('Файл', {})) or self._extract_url(props.get('URL', {}))
            yadisk_path = ""
            if file_url and (file_url.startswith("https://yadi.sk/d/") or file_url.startswith("https://disk.yandex.ru/d/")):
                # Пытаемся получить jpeg из папки по публичной ссылке
                yadisk_path = self.get_first_jpeg_in_yadisk_folder(file_url)
            else:
                filename = self._extract_filename_from_url(file_url)
                if filename and filename.lower().endswith('.jpg'):
                    yadisk_path = self.find_yadisk_path_by_name(filename)
            if not yadisk_path:
                print(f"❌ Не найден jpeg для карточки {idea['id']}")
                continue
            preview_url = self.publish_and_get_preview(yadisk_path)
            if not preview_url:
                print(f"❌ Нет preview/public_url для {yadisk_path}")
                continue
            try:
                print(f"➡️ Обновляю поле 'Файл' для {idea['id']}: {preview_url}")
                await self.notion.pages.update(
                    page_id=idea['id'],
                    properties={
                        'Файл': {
                            'type': 'files',
                            'files': [
                                {'type': 'external', 'name': yadisk_path.split('/')[-1], 'external': {'url': preview_url}}
                            ]
                        }
                    }
                )
                print(f"✅ Картинка применена для {idea['id']}: {preview_url}")
                applied += 1
            except Exception as e:
                print(f"❌ Ошибка применения картинки для {idea['id']}: {e}")
        print(f"\nИтого обновлено карточек: {applied}/{len(resp.get('results', []))}")

    def _extract_url(self, prop: dict) -> str:
        # Вытаскивает url из поля типа files/url/text
        if not prop:
            return ''
        if prop.get('type') == 'files' and prop.get('files'):
            for f in prop['files']:
                if f.get('type') == 'external':
                    return str(f['external'].get('url', '') or '')
                if f.get('type') == 'file':
                    return str(f['file'].get('url', '') or '')
        if prop.get('type') == 'url':
            return str(prop.get('url', '') or '')
        if prop.get('type') == 'rich_text':
            rich = prop.get('rich_text')
            if not rich or not isinstance(rich, list) or not rich:
                return ''
            plain = rich[0].get('plain_text', '')
            if plain is None:
                return ''
            return str(plain)
        return ''

    def _extract_filename_from_url(self, url: str) -> str:
        import urllib.parse
        path = urllib.parse.urlparse(url).path
        if not path:
            return ""
        fname = path.split("/")[-1]
        return str(fname or "")

    def find_yadisk_path_by_basename(self, basename: str, start_folder: str = "/") -> str:
        start_folder = str(start_folder or "/")
        basename = str(basename or "")
        exts = [".jpg", ".jpeg", ".png"]
        print(f"🔍 Ищу файл по basename {basename} в {start_folder}")
        try:
            for item in self.yadisk.listdir(start_folder):
                name = str(item.name or "")
                if item.type == "file" and any(name.startswith(basename) and name.lower().endswith(ext) for ext in exts):
                    print(f"✅ Найден файл: {item.path}")
                    return str(item.path or "")
                elif item.type == "dir":
                    found = self.find_yadisk_path_by_basename(basename, str(item.path or "/"))
                    if found:
                        return str(found or "")
        except Exception as e:
            print(f"Ошибка обхода {start_folder}: {e}")
        return ""

    async def batch_apply_yadisk_jpeg_by_name_field(self, limit=20):
        resp = await self.notion.databases.query(
            database_id=str(self.ideas_db_id),
            page_size=limit,
            sorts=[{"property": "Created time", "direction": "descending"}]
        )
        applied = 0
        for idea in resp.get('results', []):
            props = idea.get('properties', {})
            name_field = self._extract_title(props.get('Name', {}))
            if not name_field:
                continue
            basename = name_field.strip().split()[0]
            print(f"\n=== Обработка карточки {idea['id']} с basename {basename} ===")
            yadisk_path = self.find_yadisk_path_by_basename(basename)
            if not yadisk_path:
                print(f"❌ Файл с basename {basename} не найден на Яндекс.Диске")
                continue
            preview_url = self.publish_and_get_preview(yadisk_path)
            if not preview_url:
                print(f"❌ Нет preview/public_url для {yadisk_path}")
                continue
            try:
                print(f"➡️ Обновляю поле 'Файл' для {idea['id']}: {preview_url}")
                await self.notion.pages.update(
                    page_id=idea['id'],
                    properties={
                        'Файл': {
                            'type': 'files',
                            'files': [
                                {'type': 'external', 'name': basename, 'external': {'url': preview_url}}
                            ]
                        }
                    }
                )
                print(f"✅ Картинка применена для {idea['id']}: {preview_url}")
                applied += 1
            except Exception as e:
                print(f"❌ Ошибка применения картинки для {idea['id']}: {e}")
        print(f"\nИтого обновлено карточек: {applied}/{len(resp.get('results', []))}")

    async def set_test_cover_for_ideas(self, test_image_url: str, limit: int = 1):
        resp = await self.notion.databases.query(
            database_id=str(self.ideas_db_id),
            page_size=limit,
            sorts=[{"property": "Created time", "direction": "descending"}]
        )
        applied = 0
        for idea in resp.get('results', []):
            try:
                print(f"➡️ Ставлю тестовую обложку для {idea['id']}: {test_image_url}")
                await self.notion.pages.update(
                    page_id=idea['id'],
                    cover={
                        "type": "external",
                        "external": {"url": test_image_url}
                    }
                )
                print(f"✅ Тестовая обложка применена для {idea['id']}")
                applied += 1
            except Exception as e:
                print(f"❌ Ошибка применения тестовой обложки для {idea['id']}: {e}")
        print(f"\nИтого обновлено тестовых обложек: {applied}/{len(resp.get('results', []))}")

    async def set_yadisk_image_as_cover_or_file(self, yadisk_public_url: str, limit: int = 1):
        # Получает preview/public_url и ставит как cover, в поле 'Файл' и в rich_text (описание)
        try:
            meta = self.yadisk.get_meta(yadisk_public_url)
            if getattr(meta, 'type', None) != 'file':
                print(f"❌ Ссылка не на файл: {yadisk_public_url}")
                return
            preview_url = getattr(meta, 'preview', None) or getattr(meta, 'public_url', None)
            if not preview_url:
                print(f"❌ Нет preview/public_url для {yadisk_public_url}")
                return
        except Exception as e:
            print(f"❌ Не удалось получить метаданные для {yadisk_public_url}: {e}")
            return
        # Обновляем первые N карточек базы идей
        resp = await self.notion.databases.query(
            database_id=str(self.ideas_db_id),
            page_size=limit,
            sorts=[{"property": "Created time", "direction": "descending"}]
        )
        applied = 0
        for idea in resp.get('results', []):
            try:
                print(f"➡️ Ставлю картинку из Яндекс.Диска для {idea['id']}: {preview_url}")
                await self.notion.pages.update(
                    page_id=idea['id'],
                    cover={
                        "type": "external",
                        "external": {"url": preview_url}
                    },
                    properties={
                        'Файл': {
                            'type': 'files',
                            'files': [
                                {'type': 'external', 'name': getattr(meta, 'name', 'image'), 'external': {'url': preview_url}}
                            ]
                        },
                        'Описание': {
                            'type': 'rich_text',
                            'rich_text': [
                                {"type": "text", "text": {"content": preview_url}}
                            ]
                        }
                    }
                )
                print(f"✅ Картинка из Яндекс.Диска применена для {idea['id']}")
                applied += 1
            except Exception as e:
                print(f"❌ Ошибка применения картинки для {idea['id']}: {e}")
        print(f"\nИтого обновлено карточек: {applied}/{len(resp.get('results', []))}")

    # ===== BRANDING SYSTEM METHODS =====
    
    async def process_branding_materials(self, limit: int = 20):
        """Обрабатывает материалы для брендинга с автоматическими обложками"""
        print("🎨 ОБРАБОТКА МАТЕРИАЛОВ БРЕНДИНГА")
        print("=" * 50)
        
        # Получаем материалы с брендингом
        materials = await self._get_branding_materials(limit)
        
        if not materials:
            print("⚠️ Материалы брендинга не найдены")
            return
        
        print(f"📊 Найдено {len(materials)} материалов брендинга")
        
        processed = 0
        for material in materials:
            success = await self._process_single_branding_material(material)
            if success:
                processed += 1
        
        print(f"✅ Обработано материалов: {processed}/{len(materials)}")
    
    async def _get_branding_materials(self, limit: int) -> List[Dict]:
        """Получает материалы с тегами брендинга"""
        try:
            # Используем базу материалов вместо идей
            materials_db = os.getenv("MATERIALS_DB", "1d9ace03-d9ff-8041-91a4-d35aeedcbbd4")
            
            # Ищем материалы с тегами брендинга
            response = await self.notion.databases.query(
                database_id=materials_db,
                page_size=limit,
                filter={
                    "or": [
                        {
                            "property": "Теги",
                            "multi_select": {
                                "contains": "брендинг"
                            }
                        },
                        {
                            "property": "Теги", 
                            "multi_select": {
                                "contains": "branding"
                            }
                        },
                        {
                            "property": "Теги",
                            "multi_select": {
                                "contains": "логотип"
                            }
                        },
                        {
                            "property": "Теги",
                            "multi_select": {
                                "contains": "дизайн"
                            }
                        }
                    ]
                },
                sorts=[{"property": "Created time", "direction": "descending"}]
            )
            
            return response.get("results", [])
            
        except Exception as e:
            print(f"❌ Ошибка получения материалов: {e}")
            return []
    
    async def _process_single_branding_material(self, material: Dict) -> bool:
        """Обрабатывает один материал брендинга"""
        try:
            material_id = material.get("id")
            properties = material.get("properties", {})
            
            # Получаем название
            name_prop = properties.get("Name", {})
            title = ""
            if "title" in name_prop and name_prop["title"]:
                title = name_prop["title"][0]["text"]["content"]
            
            print(f"🔄 Обработка материала: {title}")
            
            # Проверяем URL поля
            url_prop = properties.get("URL", {})
            url = url_prop.get("url", "") if "url" in url_prop else ""
            
            # Проверяем Files & media
            files_prop = properties.get("Files & media", {})
            files_url = ""
            if "files" in files_prop and files_prop["files"]:
                for file in files_prop["files"]:
                    if file.get("type") == "external":
                        files_url = file["external"]["url"]
                        break
            
            # Определяем источник для обложки
            cover_url = None
            source_type = "unknown"
            
            if url:
                if "figma.com" in url:
                    cover_url = url
                    source_type = "figma"
                    print(f"🎨 Найден Figma URL: {url}")
                elif "yadi.sk" in url or "disk.yandex.ru" in url:
                    cover_url = url
                    source_type = "yandex_disk"
                    print(f"☁️ Найден Яндекс.Диск URL: {url}")
                elif "prnt.sc" in url or "lightshot.cc" in url:
                    cover_url = url
                    source_type = "screenshot"
                    print(f"📸 Найден скриншот URL: {url}")
                elif any(ext in url.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                    cover_url = url
                    source_type = "direct_image"
                    print(f"🖼️ Найден прямой URL изображения: {url}")
            
            elif files_url:
                if "figma.com" in files_url:
                    cover_url = files_url
                    source_type = "figma"
                    print(f"🎨 Найден Figma URL в Files: {files_url}")
                elif "yadi.sk" in files_url or "disk.yandex.ru" in files_url:
                    cover_url = files_url
                    source_type = "yandex_disk"
                    print(f"☁️ Найден Яндекс.Диск URL в Files: {files_url}")
            
            # Применяем обложку
            if cover_url and material_id:
                success = await self._apply_cover_by_type(material_id, cover_url, source_type)
                if success:
                    print(f"✅ Обложка применена для {title}")
                    return True
                else:
                    print(f"⚠️ Не удалось применить обложку для {title}")
            else:
                print(f"⚠️ Не найден подходящий URL для {title}")
            
            return False
            
        except Exception as e:
            print(f"❌ Ошибка обработки материала: {e}")
            return False
    
    async def _apply_cover_by_type(self, page_id: str, url: str, source_type: str) -> bool:
        """Применяет обложку в зависимости от типа источника"""
        try:
            if source_type == "figma":
                return await self.apply_figma_cover(page_id, url)
            elif source_type == "yandex_disk":
                return await self.apply_cover_from_yadisk_url(page_id, url)
            elif source_type == "screenshot":
                # Для скриншотов используем универсальный метод
                return await self.apply_cover_from_url(page_id, url)
            elif source_type == "direct_image":
                # Для прямых изображений используем универсальный метод
                return await self.apply_cover_from_url(page_id, url)
            else:
                print(f"⚠️ Неизвестный тип источника: {source_type}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка применения обложки: {e}")
            return False

if __name__ == "__main__":
    manager = MediaCoverManager()
    async def main():
        await manager.batch_apply_covers_by_filename(limit=20)
    asyncio.run(main()) 