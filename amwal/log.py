import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        "%(levelname)s|%(asctime)s|%(message)s", datefmt="%m/%d/%Y %H:%M:%S"
    )
)
logger.addHandler(handler)
