from datetime import date
from pathlib import Path
from loguru import logger


class DatesLogger:
    __singleton_alive = False
    __LOG_FILE_NAME = "processed_dates.txt"
    __FAIL_IDS_FILE_NAME = "failured_ids.txt"

    def __init__(self):
        if DatesLogger.__singleton_alive:
            raise PermissionError("This singleton already exists")
        self.dates_from_logs = list()
        DatesLogger.__singleton_alive = True

    def read_logs(self):
        DatesLogger.__check_logging_file()
        with open(DatesLogger.__LOG_FILE_NAME, "r") as fp:
            self.dates_from_logs = [self.__convert_string_into_date(x) for x in fp.readlines()]
        return self.dates_from_logs

    @staticmethod
    def __check_logging_file():
        if Path(DatesLogger.__LOG_FILE_NAME).exists():
            logger.info(f"{DatesLogger.__LOG_FILE_NAME} file exists")
        else:
            with open(DatesLogger.__LOG_FILE_NAME, "w"):
                logger.info(f"{DatesLogger.__LOG_FILE_NAME} file created")

    def write(self, log: date):
        with open(self.__LOG_FILE_NAME, "a") as fp:
            fp.write(f"{self.__convert_date_into_string(log)}\n")
            logger.info(f"{log} written")

    def write_exception(self, exception: int | str):
        with open(self.__FAIL_IDS_FILE_NAME, "a") as fp:
            fp.write(str(exception))

    @staticmethod
    def __convert_date_into_string(date_to_convert: date) -> str:
        return date_to_convert.isoformat()

    @staticmethod
    def __convert_string_into_date(date_to_convert: str) -> date:
        return date.fromisoformat(date_to_convert)

    def dispose(self):
        DatesLogger.__singleton_alive = False
        del self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dispose()
