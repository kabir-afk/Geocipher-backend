FROM python:3.12-alpine3.23

WORKDIR /app

RUN python -m venv venv

RUN source venv/bin/activate

COPY backend /app/backend

RUN cd /app/backend && pip install -r requirements.txt

RUN cd /app/backend && python manage.py migrate

CMD ["python" , "/app/backend/manage.py" , "runserver" ,"0.0.0.0:8000"]