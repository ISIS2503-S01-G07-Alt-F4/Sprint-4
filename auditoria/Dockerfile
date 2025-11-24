FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt --no-cache-dir

CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8000"]