from datetime import date, timedelta
from pprint import pprint
from loguru import logger
from typing import Generator, Optional, Self

from dates_logger import DatesLogger
from pyrus_client import PyrusClient
from equalizer import Equalizer


FORM_IDS = [522023]  # TODO: make config and read it from it


class TicketTerminator:

    __HOUR_PAIRS_OF_DAY = (("00", "03"), ("04", "07"), ("08", "11"), ("12", "15"), ("16", "19"), ("20", "23"))

    def __init__(self, pyrus_cred_path: str):
        logger.add("deleted_ticket_ids.txt", format="{message}", level="DEBUG")
        self.__pyrus_credential_path: str = pyrus_cred_path
        self.__pyrus_client: PyrusClient = self.__configure_pyrus_client()
        self.__processed_dates: Optional[list[date]] = None
        self.__dates: list[date] = list()
        self.__termination_delay: int | float = 1
        self.forms_to_clean_ids: list[int] = list()
        self.__days_to_preserve: int = 365 * 2

    def preserve(self, days: int) -> Self:
        self.__days_to_preserve = days
        return self

    def with_termination_delay(self, delay: float | int) -> Self:
        self.__termination_delay = delay
        return self

    def to_clean(self, form_ids: list[int]) -> Self:
        self.forms_to_clean_ids.extend(form_ids)
        return self

    def get_dates_to_terminate(self) -> Self:
        with DatesLogger() as log_manager:
            self.__processed_dates = log_manager.read_logs()
            start_date: date = self.__calculate_start_date()
        days_to_delete_amount = ((date.today() - timedelta(days=self.__days_to_preserve)) - start_date).days
        days: list[date] = list()
        for days_increment in range(days_to_delete_amount):
            days.append(start_date + timedelta(days=days_increment))
        self.__dates = days
        return self

    def __calculate_start_date(self) -> date:
        if self.__processed_dates:
            return self.__processed_dates[-1]
        else:
            return date.fromisoformat(input('write here the creation date of the first ticket '
                                            'in the register in ISO format like:\n2018-06-18\n\n'
                                            'here, please: '))

    def inspect(self) -> Self:
        print("FIRST 100 DATES")
        print("#" * 30)
        pprint(self.__dates[:100:])
        print("#" * 30)
        print("LAST 100 DATES")
        print("#" * 30)
        pprint(self.__dates[len(self.__dates) - 100::])
        print("#" * 30)
        input("IF DATES ARE CORRECT - PRESS ENTER       \n"
              "                                         \n"
              "       !!!!!!CAUTION!!!!!!               \n"
              "       !!!!!!CAUTION!!!!!!               \n"
              "       !!!!!!CAUTION!!!!!!               \n"
              "                                         \n"
              "IT WILL LAUNCH TICKET TERMINATION PROCESS\n")
        return self

    def terminate_tickets(self):
        with DatesLogger() as log_manager:
            for day in self.__dates:
                logger.info(f"terminating tickets of {day.isoformat()}...")
                self.__terminate_tickets_by(day, log_manager)
                logger.info(f"ticket of {day.isoformat()} are terminated")
                log_manager.write(day)

    def __configure_pyrus_client(self) -> PyrusClient:
        """
        [0] - login
        [1] - security key
        :return: PyrusClient instance
        """
        with open(self.__pyrus_credential_path, "r") as fp:
            credentials = fp.readlines()
        return PyrusClient(credentials[0], credentials[1]).authenticate()

    def __terminate_tickets_by(self, day: date, log_manager: DatesLogger) -> None:
        logger.info(f"collecting tickets for {day.isoformat()}")
        ticket_ids = self.__get_ticket_ids(day)
        for ticket_id in ticket_ids:
            with Equalizer(seconds=self.__termination_delay, log_manager=log_manager):
                self.__pyrus_client.delete_ticket(ticket_id)
                logger.debug(f"{day.isoformat().center(20)}: ticket with id {ticket_id} deleted")

    def __get_ticket_ids(self, day: date) -> Generator:
        tickets_json = list()
        for form_id in FORM_IDS:
            logger.info(f"collecting tickets of {form_id}")
            tickets_json.extend(self.__collect_tickets(day, form_id))
            logger.info(f"tickets of {form_id} are collected")
        return (x["id"] for x in tickets_json)

    def __collect_tickets(self, day, form_id):
        collected_tickets = list()
        for hour_pair in self.__HOUR_PAIRS_OF_DAY:
            logger.info(f"collecting tickets from {hour_pair[0]} to {hour_pair[1]}...")
            try:
                collected_tickets.extend(self.__pyrus_client.get_register(form_id, day, hour_pair)["tasks"])
                logger.info("tickets collected")
            except Exception as ex:
                logger.error(ex)
        return collected_tickets
