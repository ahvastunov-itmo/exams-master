from random import randint
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
		self._tickets = [Ticket('test1'), Ticket('test2')]
		self._number_of_tickets = 2


	def loadTickets(self, url):
		# ~~~~
		return


	def getNumberOfTickets(self):
		return self._number_of_tickets

	def getTicket(self, number):
		if (number < self._number_of_tickets):
			return self._tickets[number]
		else:
			# Indexoutofrange
			return False

	def getRandomFreeTicket(self):
		while (True):
			i = randint(0, self.getNumberOfTickets() - 1)
			if self._tickets[i].isFree():
				return self._tickets[i]


TicketsAPI = Tickets()










