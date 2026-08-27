"""SevaSetu AI — Logging Configuration | Rahul Jha | Made in India 🇮🇳"""
import logging, sys
from app.core.config import settings

def setup_logging():
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
        format=fmt,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
