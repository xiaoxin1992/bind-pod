import logging


class Logger:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def print(self, msg, level="info"):
        return getattr(self.logger, level, 'info')(msg)

