import os
import asyncio
from typing import List, Dict
from dotenv import load_dotenv
from notion_client import AsyncClient
import yadisk

load_dotenv()

class MediaCoverManager:
    def __init__(self):
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.ideas_db_id = os.getenv("NOTION_IDEAS_DB_ID")
        self.yadisk_token = os.getenv("YA_ACCESS_TOKEN")
        if not self.notion_token:
            raise RuntimeError("NOTION_TOKEN не найден в env")
        if not self.ideas_db_id:
            raise RuntimeError("NOTION_IDEAS_DB_ID не найден в env")
        if not self.yadisk_token:
            raise RuntimeError("YA_ACCESS_TOKEN не найден в env")
        self.notion = AsyncClient(auth=str(self.notion_token))
        self.yadisk = yadisk.YaDisk(token=str(self.yadisk_token))

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
            preview = meta.get('preview')
            if preview:
                return preview
        except Exception as e:
            print(f"   ⚠️ Не удалось получить preview для {public_url}: {e}")
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
            return bool(meta.get('public_url'))
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
        print(f"⏩ Публикую и получаю preview для {yadisk_path}")
        try:
            if not self.is_published(yadisk_path):
                self.yadisk.publish(yadisk_path)
                print(f"🌍 Файл опубликован: {yadisk_path}")
            meta = self.yadisk.get_meta(yadisk_path)
            preview = meta.get('preview')
            public_url = meta.get('public_url', '')
            print(f"   preview: {preview}")
            print(f"   public_url: {public_url}")
            if preview:
                return preview
            if public_url:
                print(f"⚠️ Preview нет, использую public_url: {public_url}")
                return public_url
            print(f"❌ Нет preview и public_url для {yadisk_path}")
            return ''
        except Exception as e:
            print(f"⚠️ Не удалось опубликовать/получить preview для {yadisk_path}: {e}")
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
            if meta['type'] == 'dir':
                folder_path = meta['path']
                for item in self.yadisk.listdir(folder_path):
                    name = str(item.name or "")
                    if item.type == "file" and name.lower().endswith(('.jpg', '.jpeg', '.png')):
                        print(f"✅ Первый jpeg в папке {folder_path}: {item.path}")
                        return str(item.path or "")
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
            if meta['type'] != 'file':
                print(f"❌ Ссылка не на файл: {yadisk_public_url}")
                return
            preview_url = meta.get('preview') or meta.get('public_url')
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
                                {'type': 'external', 'name': meta.get('name', 'image'), 'external': {'url': preview_url}}
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

if __name__ == "__main__":
    manager = MediaCoverManager()
    async def main():
        await manager.batch_apply_covers_by_filename(limit=20)
    asyncio.run(main()) 