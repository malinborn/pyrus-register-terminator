import json
from ticket_terminator import TicketTerminator


def main():
    with open("config.json", "r") as fp:
        config = json.load(fp)

    ticket_termination = TicketTerminator(config["pyrus_credentials_path"])\
        .to_clean(config["form_ids_to_clean"])\
        .with_termination_delay(config["ticket_termination_delay"])\
        .preserve(config["days_to_preserve"])

    ticket_termination\
        .get_dates_to_terminate()\
        .inspect()\
        .terminate_tickets()


if __name__ == "__main__":
    main()
