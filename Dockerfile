FROM python:3.11-slim

# ffmpeg is required by yt-dlp (audio extraction) and py-tgcalls (VC streaming)
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render's Web Service injects $PORT at runtime; main.py binds a tiny
# health-check HTTP server to it so the service passes Render's port scan.
ENV PORT=10000
EXPOSE 10000

CMD ["python3", "main.py"]
