from datetime import date, timedelta
from pprint import pprint
from loguru import logger
from typing import Generator

from dates_logger import DatesLogger
from pyrus_client import PyrusClient
from equalizer import Equalizer


def get_dates_to_terminate() -> list[date]:
    with DatesLogger() as log_manager:
        start_date: date = __calculate_start_date(log_manager.read_logs())
    days_to_delete_amount = ((date.today() - timedelta(days=(365 * 2))) - start_date).days
    days: list[date] = list()
    for days_increment in range(days_to_delete_amount):
        days.append(start_date + timedelta(days=days_increment))
    return days


def __calculate_start_date(used_dates: list[date]) -> date:
    if used_dates:
        return used_dates[-1]
    else:
        return date.fromisoformat("2018-06-18")  # first ticket creation date


def inspect(dates: list[date]) -> None:
    print("FIRST 100 DATES")
    print("#" * 30)
    pprint(dates[:100:])
    print("#" * 30)
    print("LAST 100 DATES")
    print("#" * 30)
    pprint(dates[len(dates) - 100::])
    print("#" * 30)
    input("IF DATES ARE CORRECT - PRESS ENTER     \n"
          "                                       \n"
          "       !!!!!!CAUTION!!!!!!             \n"
          "       !!!!!!CAUTION!!!!!!             \n"
          "       !!!!!!CAUTION!!!!!!             \n"
          "                                       \n"
          "IT WILL LAUNCH TICKET TERMINATION PROCESS")


def terminate_tickets(days: list[date]):
    pyrus_client = PyrusClient()
    with DatesLogger() as log_manager:
        for day in days:
            __terminate_tickets_by(day, pyrus_client, log_manager)
            logger.info(f"ticket of {day.isoformat()} are terminated")
            log_manager.write(day)


def __terminate_tickets_by(day: date, pyrus_client: PyrusClient, log_manager: DatesLogger) -> None:
    ticket_ids = __get_ticket_ids(day, pyrus_client)
    for ticket_id in ticket_ids:
        with Equalizer(seconds=1, log_manager=log_manager):
            pyrus_client.delete_ticket(ticket_id)


def __get_ticket_ids(day: date, pyrus_client: PyrusClient) -> Generator[int]:
    ...


def main():
    dates_to_delete = get_dates_to_terminate()
    inspect(dates_to_delete)
    terminate_tickets(dates_to_delete)


if __name__ == "__main__":
    main()
