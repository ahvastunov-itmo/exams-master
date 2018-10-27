from flask import Flask, redirect, render_template, request, session, url_for
from sqlalchemy.orm import sessionmaker
from tableusersdef import *
from tablehistorydef import *
from tickets import *


app = Flask(__name__)
app.secret_key = 'veryverysecretkey1'


@app.route('/')
def index():
	# index
	# -------------------------------------

	return (render_template('index.html') if session.get('logged_in')
	else redirect(url_for('login')))


@app.route('/login', methods=['POST', 'GET'])
def login():
	# shows login form and handles login and registration
	# --------------------------------------

	if request.method == 'POST':
		username = str(request.form['username'])

		# search for username in database
		result = checkUser(username, users_engine, User)
		if not result:
			# register new user
			registerUser(username)

		session['logged_in'] = True
		session['username'] = username

		return redirect(url_for('index'))

	else:
		return render_template('login.html')


@app.route('/logout')
def logout():
	# ends session and deletes username
	# ------------------------------------

	session['logged_in'] = False
	session.pop('username', None)
	return redirect(url_for('index'))


@app.route('/random')
def random():
	# generates random ticket number and adds to the history
	# -----------------------------------------------

	if not session.get('logged_in'):
		return redirect(url_for('login'))
	else:
		if not TicketsAPI.ticketsLoaded():
			return redirect(url_for('load'))
		# check if we already gave random number to this student
		username = session['username']
		result = checkUser(username, history_engine, Entry)
		if result:
			ticket = TicketsAPI.getTicket(0, result.number)
			return render_template('random.html', number=result.number, url=ticket.getUrl())
		else:
			# give random ticket to a student
			# Doesn't use exam parameters yet
			username = session['username']
			number, url = giveRandomTicket(username)

			return render_template('random.html', number=number, url=url)


@app.route('/load')
def load():
	# loads ticket lists from json
	# -------------------------------

	TicketsAPI.loadTickets('multilist.json')
	return redirect(url_for('index'))


@app.route('/finished', methods=['POST', 'GET'])
def finished():
	# saves exam results
	# -----------------------

	if request.method == 'POST':
		username = str(request.form['username'])
		listnumber = int(request.form['listnumber'])
		ticketnumber = int(request.form['number'])
		time = str(request.form['time'])

		TicketsAPI.results.append(repr([username, listnumber, ticketnumber, time]))

		return redirect(url_for('index'))

	else:
		return render_template('finished.html')


@app.route('/history')
def history():
	# print results
	# --------------------------

	return render_template('history.html', hist=TicketsAPI.results)


def checkUser(username, engine, dbName):
	# Checks if user in database

	Session = sessionmaker(bind=engine)
	session = Session()

	query = session.query(dbName).filter(dbName.username.in_([username]))
	result = query.first()

	return result


def registerUser(username):

	Session = sessionmaker(bind=users_engine)
	session = Session()

	user = User(username)
	session.add(user)
	session.commit()


def giveRandomTicket(username):

	ticket = TicketsAPI.getRandomFreeTicket(0)
	ticket.giveTo(username)
	number = ticket.getNumber()

	Session = sessionmaker(bind=history_engine)
	session = Session()

	entry = Entry(username, number)

	session.add(entry)
	session.commit()

	return number, ticket.getUrl()
