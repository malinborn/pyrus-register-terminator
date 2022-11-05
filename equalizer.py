from datetime import datetime
from time import sleep
from types import TracebackType
from loguru import logger

from dates_logger import DatesLogger


class Equalizer:
    def __init__(self, seconds: int, log_manager: DatesLogger):
        self.minimum_delay = seconds
        self.started_execution = datetime.now()
        self.log_manager = log_manager

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb: TracebackType):
        if all((exc_type, exc_val, exc_tb)):
            logger.error(f"{exc_type.__name__}, {exc_val}, {exc_tb.tb_frame}")
            self.log_manager.write_exception(f"{exc_type.__name__}, {exc_val}, {exc_tb.tb_frame}")
        else:
            self.__equalize()

    def __equalize(self):
        self.finished_execution = datetime.now()
        execution_time = self.finished_execution - self.started_execution
        if execution_time.seconds < self.minimum_delay:
            sleep(self.minimum_delay - execution_time.seconds)
