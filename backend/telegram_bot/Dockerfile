FROM python:3.9-slim

WORKDIR /app

COPY requirements/base.txt .
COPY requirements/bot.txt .

RUN pip install --no-cache-dir -r bot.txt

COPY . .

CMD ["python", "telegram_bot/bot.py"]