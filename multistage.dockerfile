FROM python:3.12-slim-trixie AS builder
WORKDIR /app

COPY backend/ .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

FROM gcr.io/distroless/python3-debian13
WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app
ENV PATH="/opt/venv/bin:$PATH"

CMD ["sh", "-c", "python manage.py migrate && python manage.py loaddata api/fixtures/coordinates.json && exec python manage.py runserver 0.0.0.0:8000"]