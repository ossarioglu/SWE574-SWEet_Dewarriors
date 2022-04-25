FROM python:3.8.0-alpine
ENV PYTHONUNBUFFERED = 1
WORKDIR /usr/src/app
COPY requirements.txt requirements.txt
RUN python3 -m pip install --upgrade pip

RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev
RUN apk add -u zlib-dev jpeg-dev gcc musl-dev
RUN python3 -m pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python3","manage.py","createsuperuser"]
CMD ["python3","manage.py","runserver","0.0.0.0:80"]