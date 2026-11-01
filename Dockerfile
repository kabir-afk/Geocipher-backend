FROM python:3.12-alpine3.23

WORKDIR /app

COPY backend .

RUN pip install -r requirements.txt && python manage.py migrate

CMD ["python" , "manage.py" , "runserver" ,"0.0.0.0:8000"]