import json
from pathlib import Path

from amwal.config import *


class JsonCache:
    def __init__(
        self, cache_dir="boursa_cache", file_extension=".json",
    ):
        self.cache_dir = Path(cache_dir)
        self.serialize = json.dumps
        self.deserialize = json.loads
        self.file_extension = file_extension
        self.enabled = True

    def disable(self):
        logger.info("cache turned off")
        self.enabled = False

    def enable(self):
        logger.info("cache turned off")
        self.enabled = True

    def add_resource(self, id_, resource):
        if not self.enabled:
            return
        with (self.cache_dir / (id_ + self.file_extension)).open("w+") as file:
            logger.info(f"Add {id_} to cache")
            file.write(self.serialize(resource))

    def get_resource(self, id_):
        if not self.enabled:
            return
        if not self.cache_dir.exists():
            self.cache_dir.mkdir()
        if not list(self.cache_dir.glob(id_ + self.file_extension)):
            logger.info(f"Cache miss for {id_}")
            return None
        with (self.cache_dir / (id_ + self.file_extension)).open() as file:
            logger.info(f"Cache hit for {id_}")
            return self.deserialize(file.read())
