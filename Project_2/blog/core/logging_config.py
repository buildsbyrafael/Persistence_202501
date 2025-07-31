from loguru import logger
import sys
import logging
from core.config import settings


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.log(level, record.getMessage())


def setup_logging():
    logger.remove()

    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level=settings.LOG_LEVEL,
    )

    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        enqueue=True,
        level=settings.LOG_LEVEL,
        backtrace=True,
        diagnose=True,
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(logger_name).handlers = [InterceptHandler()]