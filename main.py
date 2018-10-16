from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from random import randint
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

	if not session.get('logged_in'):
		return redirect(url_for('login'))
	else:
		return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
	# shows login form and handles login and registration
	# --------------------------------------

	if request.method == 'POST':
		USERNAME = str(request.form['username'])

		# search for username in database
		Session = sessionmaker(bind=users_engine)
		s = Session()
		query = s.query(User).filter(User.username.in_([USERNAME]))
		result = query.first()
		if not result:		
			# register new user
			user = User(USERNAME)
			s.add(user)
			s.commit()
			
		session['logged_in'] = True
		session['username'] = USERNAME

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
		# check if we already gave random number to this student
		Session = sessionmaker(bind=history_engine)
		s = Session()
		username = session['username']
		query = s.query(Entry).filter(Entry.username.in_([username]))
		result = query.first()
		if result:
			return render_template('random.html', number=result.number)
		else:
			# give random ticket to a student
			# Doesn't use exam parameters yet
			

			ticket = TicketsAPI.getRandomFreeTicket(0)
			ticket.giveTo(username)
			number = ticket.getNumber()


			Session = sessionmaker(bind=history_engine)
			s = Session()

			username = session['username']
			entry = Entry(username, number)

			s.add(entry)
			s.commit()

			return render_template('random.html', number=number)



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
