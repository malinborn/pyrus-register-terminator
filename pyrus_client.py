import requests

from typing import Self
from datetime import date


class PyrusClient:
    def __init__(self, login: str, security_key: str):
        self.token = None
        self.login = login
        self.security_key = security_key

    def authenticate(self) -> Self:
        response = requests.post('https://api.pyrus.com/v4/auth',
                                 headers=self.__set_headers(),
                                 json={'login': self.login,
                                       'security_key': self.security_key})
        self.token = f'Bearer {response.json()["access_token"]}'
        return self

    def get_register(self, form_id: int, day: date, hours: tuple[str, str]) -> dict:
        response = requests.post(f"https://api.pyrus.com/v4/forms/{form_id}/register",
                                 headers=self.__set_headers(),
                                 json={"created_after": day.strftime(f"%Y-%m-%dT{hours[0]}:00:00Z"),
                                       "created_before": day.strftime(f"%Y-%m-%dT{hours[1]}:59:00Z"),
                                       "include_archived": "y",
                                       "field_ids": [1]})
        return response.json()

    def delete_ticket(self, ticket_id: int):
        response = requests.post(f"https://pyrus.com/restapi/deletetask/{ticket_id}",
                                 headers=self.__set_headers())
        return response.json()

    def __set_headers(self) -> dict[str: str]:
        if self.token:
            return {"Content-Type": "application/json",
                    "Authorization": self.token}
        else:
            return {'Content-Type': 'application/json'}
