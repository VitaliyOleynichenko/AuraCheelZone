FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python initdb/populate_db.py && gunicorn --bind 0.0.0.0:8000 \"app:create_app()\""]
