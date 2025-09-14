FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

EXPOSE 5000

ENV FLASK_APP=microblog.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]