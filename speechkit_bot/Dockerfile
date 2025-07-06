FROM python:3.10-slim

# Установим ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Установим зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код функции
COPY index.py ./

WORKDIR /

# Точка входа для Serverless Containers — запуск Flask-сервера
CMD ["python", "index.py"]