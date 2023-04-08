import redis

pool = redis.ConnectionPool(host='localhost',
                            port=6379,
                            max_connections=10,
                            socket_timeout=3)
redis_client = redis.Redis(connection_pool=pool)


def cache_get(key):
    try:
        return redis_client.get(key).decode()
    except AttributeError as e:
        print(f"Oops, no such key: {key} in cache")
        return None


def cache_set(key, value, ttl):
    try:
        redis_client.set(key, value, ex=ttl)
    except Exception as e:
        print("Error: ", e)


def get(key):
    return cache_get(key)
