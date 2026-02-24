FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
VOLUME ["/app/sticker_packs"]
EXPOSE 8080
CMD ["uvicorn", "whatsapp_api:app", "--host", "0.0.0.0", "--port", "8080"]
