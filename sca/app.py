import time, os
import socket
import redis
import psycopg2
import pika
import uuid
from flask import Flask, json, request
from flask_cors import CORS
from pathlib import Path


version = os.environ.get("VERSION")

app = Flask(__name__)
CORS(app)

def create_app():
   return app

def connect_to_redis():
    cache = redis.Redis(
        host=os.environ.get("CACHE_HOST"),
        port=os.environ.get("CACHE_PORT"),
        password=os.environ.get("CACHE_PASSWORD"),
    )
    return cache

def get_hit_count():
    retries = 5
    while True:
        try:
            return connect_to_redis().incr("hits")
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

def get_db_conn():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
    )
    return conn


@app.route("/")
def base_api():
    data = {
        "version": version,
        "hostname": socket.gethostname(),
    }
    return app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype="application/json",
    )


@app.route("/health/")
def health_api():
    data = {
        "version": version,
        "message": "RUNNING",
    }
    return app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype="application/json",
    )


@app.route("/fail/")
def fail_api():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with Werkzeug Server")
    func()

    data = {
        "version": version,
        "state": "SHUTDOWN",
    }
    return app.response_class(
        response=json.dumps(data),
        status=503,
        mimetype="application/json",
    )


@app.route("/database-connect/")
def database_connect_api():
    try:
        conn = get_db_conn()
        conn.rollback()
        cur = conn.cursor()
        cur.execute("SELECT * from {} LIMIT 20;".format("DB_SELECT_TABLE"))
        query = cur.fetchall()
        msg = query
        status_code = 200
    except Exception as e:
        msg = "[!] something bad happened: {}".format(e)
        status_code = 500

    data = {
        "version": version,
        "message": msg,
    }
    return app.response_class(
        response=json.dumps(data),
        status=status_code,
        mimetype="application/json",
    )


@app.route("/cache-connect/")
def cache_connect_api():
    try:
        msg = get_hit_count()
        status_code = 200
    except Exception as e:
        msg = "[!] something bad happened: {}".format(e)
        status_code = 500

    data = {
        "version": version,
        "message": "call count: {}".format(msg),
    }
    return app.response_class(
        response=json.dumps(data),
        status=status_code,
        mimetype="application/json",
    )


@app.route("/queue-connect/")
def queue_connect_api():
    try:
        queue_name = "sca-queue"
        queue_msg = uuid.uuid4().hex.upper()[0:6]
        credentials = pika.PlainCredentials(
            os.environ.get("RABBITMQ_USER"),
            os.environ.get("RABBITMQ_PASSWORD")
            )
        parameters = pika.ConnectionParameters(os.environ.get("RABBITMQ_HOST"),
            os.environ.get("RABBITMQ_PORT"),
            os.environ.get("RABBITMQ_VHOST"),
            credentials
            )

        connection = pika.BlockingConnection(parameters)

        channel = connection.channel()
        channel.queue_declare(queue="sca-queue")
        channel.basic_publish(exchange="", routing_key="sca-queue", body="Queued from Sample Container APP")
        connection.close()

        msg = "SUCCESSFULLY WROTE {} TO {} QUEUE.".format(queue_msg, queue_name)
        status_code = 201

    except Exception as e:
        msg = "[!] something bad happened: {}".format(e)
        status_code = 500

    data = {
        "version": version,
        "message": msg,
    }
    return app.response_class(
        response=json.dumps(data),
        status=status_code,
        mimetype="application/json",
    )


@app.route("/create-file/")
def create_file_api():
    try:
        rand_str = uuid.uuid4().hex.upper()[0:6]
        file_name = "./junk_dir/create-file-api/junk-{}.txt".format(rand_str)
        file_msg = "Junk Generated ID: {}".format(rand_str)
        Path("./junk_dir/create-file-api/").mkdir(parents=True, exist_ok=True)
        f = open(file_name, "a")
        f.write(file_msg)
        f.close()

        f = open(file_name, "r")
        file_read = f.read()
        msg = "SUCCESSFULLY WROTE << {} >> TO << {} >> AND HAS BEEN READ LIKE THIS: << {} >>".format(file_msg, file_name, file_read)
        status_code = 201

    except Exception as e:
        msg = "[!] something bad happened: {}".format(e)
        status_code = 500

    data = {
        "version": version,
        "message": msg,
    }
    return app.response_class(
        response=json.dumps(data),
        status=status_code,
        mimetype="application/json",
    )
