import os
from flask import Flask, jsonify
import redis

app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)

@app.get("/")
def index():
    try:
        visits = redis_client.incr("page_visits")
        return (
            "<!doctype html><html><head><title>Compose Lab</title></head>"
            "<body><h1>AWS Docker Compose Lab</h1>"
            f"<p>Application status: running</p><p>Visit count: {visits}</p>"
            "<p>Web app and Redis are separate Compose services.</p></body></html>",
            200,
            {"Content-Type": "text/html; charset=utf-8"},
        )
    except redis.RedisError:
        return "Web service is running, but Redis is unavailable.\n", 503

@app.get("/health")
def health():
    try:
        redis_client.ping()
        return jsonify(status="ok", redis="reachable"), 200
    except redis.RedisError:
        return jsonify(status="degraded", redis="unavailable"), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
