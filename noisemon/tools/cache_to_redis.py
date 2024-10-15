from typing import Union
import redis
import json


def get_cacher(redis_params, EXPIRE=60 * 60 * 24):
    """
    EXPIRE is in seconds
    """
    r = redis.Redis(**redis_params)

    def arguments_layer(key_argument_position=0):
        def decorator(function):
            # print(f"decorator got {function}")
            # function = function[0]
            # @wraps(function)
            def wrapper(*args, **kwargs):
                key: Union[str, int] = args[key_argument_position]
                if value := r.get(key):
                    # print(f"Got from cache {key} -> [{value}]")
                    if type(value) == bytes:
                        value = value.decode("utf8")
                    return json.loads(value)
                else:
                    value = function(*args, **kwargs)
                    if type(value) not in {int, str}:
                        r.set(key, json.dumps(value, ensure_ascii=False), ex=EXPIRE)
                    else:
                        r.set(key, value, ex=EXPIRE)
                    return value

            return wrapper

        return decorator

    return arguments_layer
