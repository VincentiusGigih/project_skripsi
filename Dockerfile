FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libx11-6 \
    libxext6 \
    libsm6 \
    libxrender1 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir dlib-bin==20.0.0
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --no-deps face-recognition==1.3.0

COPY . .

CMD ["/bin/sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-8080} --timeout 120 --workers 1"]
