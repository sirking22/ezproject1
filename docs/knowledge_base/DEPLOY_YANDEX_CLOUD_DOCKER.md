## Деплой фронта (Vite static) в Docker на Яндекс.Cloud (Compute/Server)

### Что есть
- `web/Dockerfile` — сборка статики и рантайм на `nginx`.
- `web/nginx.conf` — SPA fallback.
- Аргументы сборки:
  - `VITE_DEMO=1|0` — источник данных (моки/реальный API)
  - `VITE_API_URL` — базовый URL API

### Сборка локально
```bash
docker build -t photoguide-web:latest --build-arg VITE_DEMO=0 --build-arg VITE_API_URL=https://api.example.com ./web
docker run -d -p 8080:80 --name photoguide-web photoguide-web:latest
```

### Яндекс.Cloud (Compute Instance)
1. Установить Docker на ВМ (Ubuntu):
```bash
sudo apt update && sudo apt install -y docker.io
sudo systemctl enable --now docker
```
2. Скопировать проект или настроить CI/CD на сборку образа и пуш в Yandex Container Registry (YCR).
3. Пример пуша в YCR:
```bash
yc container registry configure-docker
docker build -t cr.yandex/${REGISTRY_ID}/photoguide-web:latest --build-arg VITE_DEMO=0 --build-arg VITE_API_URL=https://api.example.com ./web
docker push cr.yandex/${REGISTRY_ID}/photoguide-web:latest
```
4. Запуск на ВМ:
```bash
docker run -d --restart always -p 80:80 --name photoguide-web cr.yandex/${REGISTRY_ID}/photoguide-web:latest
```

### Примечания
- Для HTTPS используйте внешнюю L7 балансировку/сертификаты или заверните Nginx через Caddy/Traefik.
- В режиме `VITE_DEMO=0` фронт ожидает рабочий backend.
