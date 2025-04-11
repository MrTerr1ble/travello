FROM python:3.9-slim

WORKDIR /app

COPY requirements/base.txt .
COPY requirements/backend.txt .

RUN python -m pip install --upgrade pip && pip install -r backend.txt --no-cache-dir

RUN mkdir -p /app/scripts

COPY scripts/entrypoint.sh /app/scripts/entrypoint.sh

RUN chmod +x /app/scripts/entrypoint.sh

COPY . .

ENTRYPOINT ["/bin/bash", "/app/scripts/entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "travello.wsgi"]