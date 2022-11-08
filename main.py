from ticket_terminator import TicketTerminator


FORM_IDS = [522023]  # TODO: make config and read it from it


def main():
    ticket_termination = TicketTerminator("creds.txt").to_clean(FORM_IDS)
    ticket_termination.get_dates_to_terminate()\
                      .inspect()\
                      .terminate_tickets()


if __name__ == "__main__":
    main()
