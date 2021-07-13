import json
from pathlib import Path

from amwal.log import logger


class JsonCache:

    enabled = True
    __slots__ = ("_cache_path", "_serialize", "_deserialize", "_file_extension")
    cache_path = Path("amwal_cache")

    def __init__(self):
        print(self.cache_path)
        self._file_extension = ".json"

    def __repr__(self):
        return f"JsonCache {JsonCache.cache_path}"

    def __getitem__(self, key):
        with (JsonCache.cache_path / (key + self._file_extension)).open() as file:
            logger.info(f"Loaded {key} from disk")
            return json.loads(file.read())

    def __setitem__(self, key, value):
        if not JsonCache.cache_path.exists():
            JsonCache.cache_path.mkdir()
        with (JsonCache.cache_path / (key + self._file_extension)).open("w+") as file:
            logger.info(f"Saved {key} to disk")
            file.write(json.dumps(value))

    def __contains__(self, key):
        return bool(list(JsonCache.cache_path.glob(key + self._file_extension)))


def cached(caches):
    def decorator(func):
        def wrapper(*args, recompute=False, **kwargs):
            if "verbose" in kwargs and kwargs["verbose"]:
                logger.disabled = not kwargs["verbose"]
            val = None
            key = func.__name__
            for arg in args:
                if isinstance(arg, str):
                    key += "_" + arg
                elif isinstance(arg, int):
                    key += "_" + str(arg)
            for cache in caches:
                enabled = cache.__class__.enabled
                if not enabled:
                    continue
                if key in cache and not recompute:
                    logger.info(f"Cache hit in {cache} for {key}")
                    val = cache[key]
                    break
            if val == None:
                val = func(*args, **kwargs)
            for cache in caches:
                enabled = cache.__class__.enabled
                if not enabled:
                    continue
                if key not in cache or recompute:
                    cache[key] = val
            return val

        return wrapper

    return decorator
