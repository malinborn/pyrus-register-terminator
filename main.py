from datetime import date, timedelta
from pprint import pprint
from loguru import logger
from typing import Generator

from dates_logger import DatesLogger
from pyrus_client import PyrusClient
from equalizer import Equalizer


logger.add("deleted_ticket_ids.txt", format="{message}", level="DEBUG")

HOUR_PAIRS_OF_DAY = (("00", "03"), ("04", "07"), ("08", "11"), ("12", "15"), ("16", "19"), ("20", "23"))
FORM_IDS_TO_CLEAN = [522023]  # TODO: make config and read it from it


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
        return date.fromisoformat(input('write here the creation date of the first ticket '
                                        'in the register in ISO format like:\n2018-06-18\n\n'
                                        'here, please: '))


def inspect(dates: list[date]) -> None:
    print("FIRST 100 DATES")
    print("#" * 30)
    pprint(dates[:100:])
    print("#" * 30)
    print("LAST 100 DATES")
    print("#" * 30)
    pprint(dates[len(dates) - 100::])
    print("#" * 30)
    input("IF DATES ARE CORRECT - PRESS ENTER       \n"
          "                                         \n"
          "       !!!!!!CAUTION!!!!!!               \n"
          "       !!!!!!CAUTION!!!!!!               \n"
          "       !!!!!!CAUTION!!!!!!               \n"
          "                                         \n"
          "IT WILL LAUNCH TICKET TERMINATION PROCESS\n")


def terminate_tickets(days: list[date]):
    pyrus_client = __configure_pyrus_client("creds.txt")
    with DatesLogger() as log_manager:
        for day in days:
            logger.info(f"terminating tickets of {day.isoformat()}...")
            __terminate_tickets_by(day, pyrus_client, log_manager)
            logger.info(f"ticket of {day.isoformat()} are terminated")
            log_manager.write(day)


def __configure_pyrus_client(path: str) -> PyrusClient:
    """
    [0] - login
    [1] - security key
    :param path: path to file with pyrus credentials
    :return: PyrusClient instance
    """
    with open(path, "r") as fp:
        credentials = fp.readlines()
    return PyrusClient(credentials[0], credentials[1]).authenticate()


def __terminate_tickets_by(day: date, pyrus_client: PyrusClient, log_manager: DatesLogger) -> None:
    logger.info(f"collecting tickets for {day.isoformat()}")
    ticket_ids = __get_ticket_ids(day, pyrus_client)
    for ticket_id in ticket_ids:
        with Equalizer(seconds=1, log_manager=log_manager):
            pyrus_client.delete_ticket(ticket_id)
            logger.debug(f"{day.isoformat().center(20)}: ticket with id {ticket_id} deleted")


def __get_ticket_ids(day: date, pyrus_client: PyrusClient) -> Generator:
    tickets_json = list()
    for form_id in FORM_IDS_TO_CLEAN:
        logger.info(f"collecting tickets of {form_id}")
        tickets_json.extend(__collect_tickets(day, form_id, pyrus_client))
        logger.info(f"tickets of {form_id} are collected")
    return (x["id"] for x in tickets_json)


def __collect_tickets(day, form_id, pyrus_client):
    collected_tickets = list()
    for hour_pair in HOUR_PAIRS_OF_DAY:
        logger.info(f"collecting tickets from {hour_pair[0]} to {hour_pair[1]}...")
        try:
            collected_tickets.extend(pyrus_client.get_register(form_id, day, hour_pair)["tasks"])
            logger.info("tickets collected")
        except Exception as ex:
            logger.error(ex)
    return collected_tickets


def main():
    dates_to_delete = get_dates_to_terminate()
    inspect(dates_to_delete)
    terminate_tickets(dates_to_delete)


def test_main():
    pyrus_client = __configure_pyrus_client("creds.txt")
    ids = __get_ticket_ids(date.today() - timedelta(days=1), pyrus_client)
    for i in range(100):
        print(ids.__next__())


if __name__ == "__main__":
    main()
