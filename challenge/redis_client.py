from django.conf import settings
import redis
import json

REDIS_CONFIG = {
    'host': settings.RD_HOST,
    'port': settings.RD_PORT,
    'db': settings.RD_DB,
}

_pool = redis.ConnectionPool(**REDIS_CONFIG)

def get_redis():
    return redis.Redis(connection_pool=_pool)

def publish_event(channel: str, payload: dict):
    r = get_redis()
    r.publish(channel, json.dumps(payload))

def subscribe(channel: str):
    r = get_redis()
    pubsub = r.pubsub()
    pubsub.subscribe(channel)
    return pubsub
