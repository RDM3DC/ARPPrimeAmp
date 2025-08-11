# Minimal runtime image
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "arpprimeamp.cli", "--N", "500"]
