FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/manage.py

CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--ws", "websockets"]
