import redis
from common.config import GlobalConfig

def get_redis_conn():
    return redis.Redis(host=GlobalConfig.redis_server, port=GlobalConfig.redis_server_port)
