# Pyrus Register Terminator #

### This script is developed to keep your registers clean ###

---

When would you need it?
- You are not a big company and you wouldn't like to pay overdraft on Pyrus's memory bank;
- You want to comply with the law of your country - if it allows you to keep users' personal data only for limited time

---

### Prerequisites:
- Python 3.11+;
- Admin access to pyrus forms you want to clean;
- "creds.txt" file with your login and security key. It should contain two rows - first for the login and second for the key;
- You have installed dependencies - ```pip install requirements.txt```.
---

### Getting started

First of all - prepare config.json

It has three options to work with:

```json
{
  "pyrus_credentials_path": "creds.txt",
  "form_ids_to_clean": [123456],
  "ticket_termination_delay": 1,
  "days_to_preserve": 700
}
```
1. Path to the file with your pyrus credentials. You would better use absolute path;
2. IDs of pyrus forms, you want to clean. It has to be a list of ints;
3. Pyrus asks to delete tickets at least with one second delay. One second - is a default value of delay.
You may use any custom delay though;
4. Days those data we want to preserve. It is two years by default.

Quick start looks something like this:

```python
import json 
from ticket_terminator import TicketTerminator

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
```

We get configuration and use it to configure our termination instance first.
After that we get dates to terminate by config, than inspect if everything is ok (this operation is irreversable). 
If dates are ok - we terminate tickets by them.

---

###### Developed by Max Kovalevsky
