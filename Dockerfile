FROM python:3.12-alpine3.23

WORKDIR /app

COPY backend .

RUN pip install -r requirements.txt

CMD ["sh", "-c", "python manage.py migrate && python manage.py loaddata api/fixtures/coordinates.json && exec daphne -b 0.0.0.0 -p 8000 backend.asgi:application"]
