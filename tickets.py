from random import randint
import json
# --------------------------------



# Represents a ticket
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
			self._problems_from_each_list = int(data["problems_from_each_list"])

			self._lists = [{"name": l["name"], "tickets": [Ticket(t["url"]) for t in l["tickets"]]} for l in data["lists"]]
		self._loaded = True


	def ticketsLoaded(self):
		return self._loaded


	def getTicket(self, list_number, ticket_number):
		if (list_number < len(self._lists)) and (ticket_number < len(self._lists[list_number]["tickets"])):
			return self._lists[list_number]["tickets"][ticket_number]
		else:
			# Indexoutofrange
			return False


	def getRandomFreeTicket(self, list_number):
		while (True):
			i = randint(0, len(self._lists[list_number]["tickets"]) - 1)
			if self.getTicket(list_number, i).isFree():
				return self.getTicket(list_number, i)


TicketsAPI = Tickets()










