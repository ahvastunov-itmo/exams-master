from random import randint
import json


class Ticket:
    number = 0

    def __init__(self, url):
        self._ticket_url = url
        self._ticket_number = Ticket.number
        self._is_given = False
        self._student = None

        Ticket.number += 1

    def getNumber(self):
        return self._ticket_number

    def getUrl(self):
        return self._ticket_url

    def isGiven(self):
        return self._is_given

    def isFree(self):
        return not self.isGiven()

    def giveTo(self, student):
        self._is_given = True
        self._student = student


# API for working with tickets
class Tickets:

    def __init__(self):
        self._problems_from_each_list = 0
        self._lists = []
        self.results = []
        self._loaded = False

    def loadTickets(self, json_data):
        with open(json_data, "r") as data_file:
            data = json.load(data_file)
            self._problems_from_each_list = int(
                data["problems_from_each_list"]
            )

            self._lists = [
                {
                    "name": l["name"],
                    "tickets": [Ticket(t["url"]) for t in l["tickets"]]
                } for l in data["lists"]
            ]

        self._loaded = True

    def ticketsLoaded(self):
        return self._loaded

    def getTicket(self, list_number, ticket_number):
        if (list_number < len(self._lists)) and \
                (ticket_number < len(self._lists[list_number]["tickets"])):
            return self._lists[list_number]["tickets"][ticket_number]
        else:
            return None

    def getRandomTicket(self, list_number):
        i = randint(0, len(self._lists[list_number]["tickets"]) - 1)
        return i, self.getTicket(list_number, i)

    def getUserTickets(self):
        """Return a list of tickets for a user"""
        tickets = []
        for i in range(len(self._lists)):
            if len(self._lists[i]["tickets"]) <= self._problems_from_each_list:
                tickets.extend(self._lists[i]["tickets"])
            else:
                given = []
                while len(given) < self._problems_from_each_list:
                    number, ticket = self.getRandomTicket(i)
                    if not (number in given):
                        given.append(number)
                        tickets.append(ticket)

        return tickets


TicketsAPI = Tickets()
