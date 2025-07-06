import os
import asyncio
from datetime import datetime
import aiohttp
import aiofiles

YA_TOKEN = os.getenv('YA_ACCESS_TOKEN')
FILENAME = 'test_cover.jpg'

async def upload_and_publish():
    remote_path = f"/telegram_uploads/test_cover_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    headers = {"Authorization": f"OAuth {YA_TOKEN}"}
    async with aiofiles.open(FILENAME, 'rb') as f:
        data = await f.read()
    async with aiohttp.ClientSession() as s:
        # Получить upload url
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        params = {'path': remote_path, 'overwrite': 'true'}
        async with s.get(url, params=params, headers=headers) as r:
            up_url = (await r.json())["href"]
        # Загрузить файл
        async with s.put(up_url, data=data, headers={"Content-Type": "application/octet-stream"}) as r2:
            assert r2.status == 201, f"Upload failed: {r2.status}"
        # Публикация
        pub_url = 'https://cloud-api.yandex.net/v1/disk/resources/publish'
        await s.put(pub_url, params={'path': remote_path}, headers=headers)
        # Получить публичную ссылку
        meta_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        async with s.get(meta_url, params={'path': remote_path}, headers=headers) as m:
            meta = await m.json()
            print('PUBLIC_URL:', meta.get('public_url'))
            print('PATH:', remote_path)

if __name__ == "__main__":
    asyncio.run(upload_and_publish()) 