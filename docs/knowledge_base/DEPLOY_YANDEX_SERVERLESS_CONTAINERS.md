## Деплой в Yandex Serverless Containers (Web + API)

Предпосылки: секреты в GitHub → Settings → Secrets and variables → Actions:
- `YC_SA_JSON_KEY` — ключ сервисного аккаунта (JSON)
- `YC_REGISTRY_ID` — ID Container Registry
- (опционально) `YC_FOLDER_ID`, `YC_SA_ID`

### Web (Vite static на Nginx)
Workflow: `.github/workflows/web_ycr_build.yml`
Параметры при ручном запуске: `vite_demo=1`, `vite_api_url=`

После пуша образа:
```bash
yc serverless container create --name taskflow-web || true
yc serverless container revision deploy \
  --container-name taskflow-web \
  --image cr.yandex/${YC_REGISTRY_ID}/photoguide-web:latest \
  --service-account-id ${YC_SA_ID} \
  --cores 1 --memory 256m --execution-timeout 5s --concurrency 16 \
  --environment VITE_DEMO=1,VITE_API_URL=
yc serverless container allow-unauthenticated-invoke --name taskflow-web || true
yc serverless container get --name taskflow-web --format json | jq -r .url
```

### API (FastAPI)
Workflow: `.github/workflows/api_yc_build_deploy.yml`
Запуск: `container_name=taskflow-api`

После деплоя URL берётся из summary шага «Output URL».
