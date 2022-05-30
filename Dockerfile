FROM python:3.7-alpine

WORKDIR /code

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

RUN apk add --no-cache gcc g++ musl-dev linux-headers postgresql-dev python3-dev

COPY ./sca/requirements.txt requirements.txt

RUN pip install -r requirements.txt

EXPOSE 8080

COPY ./sca .

CMD ["waitress-serve", "--call" ,"'app:create_app'"]
