import logging


def setup_logging() -> logging.Logger:
    logger = logging.getLogger('main')
    if not logger.hasHandlers():
        level = logging.DEBUG
        logger.setLevel(level)
        file_handler = logging.FileHandler('logs.log')
        stream_handler = logging.StreamHandler()
        file_handler.setLevel(level)
        stream_handler.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("pika").setLevel(logging.WARNING)
        
    return logger

