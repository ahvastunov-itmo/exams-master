from pathlib import Path
from flask import Flask, redirect, render_template, request, session, url_for
from flask import send_file, send_from_directory, Response
from sqlalchemy.orm import sessionmaker
import tableusersdef
import tablehistorydef
from tickets import TicketsAPI
from flask_rbac import RBAC
import csv
from io import StringIO, BytesIO


app = Flask(__name__)
app.secret_key = 'veryverysecretkey1'
app.config['JSON_PATH'] = Path('json/examparams.json')
app.config['RBAC_USE_WHITE'] = True
rbac = RBAC(app)
rbac.set_role_model(tableusersdef.Role)
rbac.set_user_model(tableusersdef.User)
anonymous = tableusersdef.User('anonymous', roles=[tableusersdef.Role.get_by_name('anonymous')])

def get_current_user():
	if not session.get('logged_in'):
		return anonymous
	else:
		return checkUser(session.get('username'), tableusersdef.users_engine, tableusersdef.User)

rbac.set_user_loader(get_current_user)


@app.route('/')
@rbac.exempt
def index():
	# index
	# -------------------------------------

	return (render_template('index.html') if session.get('logged_in')
	else redirect(url_for('login')))


@app.route('/login', methods=['POST', 'GET'])
@rbac.exempt
def login():
	# shows login form and handles login and registration
	# --------------------------------------
	#global current_user

	if request.method == 'POST':
		username = str(request.form['username'])

		# search for username in database
		result = checkUser(username, tableusersdef.users_engine, tableusersdef.User)
		if not result:
			# register new user
			registerUser(username, 'student')

		session['logged_in'] = True
		session['username'] = username
		current_user = checkUser(username, tableusersdef.users_engine, tableusersdef.User)

		return redirect(url_for('index'))

	else:
		return render_template('login.html')


@app.route('/logout')
@rbac.allow(['student', 'professor', 'admin'], ['GET'])
def logout():
	# ends session and deletes username
	# ------------------------------------

	session['logged_in'] = False
	session.pop('username', None)
	return redirect(url_for('index'))


@app.route('/random')
@rbac.allow(['student'], ['GET'])
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
		result = checkUser(username, tablehistorydef.history_engine, tablehistorydef.Entry)
		if not result:
			giveRandomTickets(username)
		return render_template('random.html', tickets=getUserTickets(username))


@app.route('/load', methods=['POST', 'GET'])
@rbac.allow(['professor'], ['GET'])
def load():
	# loads ticket lists from uploaded json file
	# -------------------------------
	if request.method == 'POST':
		if 'file' not in request.files:
			app.logger.warning('No file part')
			return redirect(request.url)
		file = request.files['file']
		if not file.filename:
			app.logger.warning('No selected file')
			return redirect(request.url)

		filepath = str(app.config['JSON_PATH'])
		file.save(filepath)

		TicketsAPI.loadTickets(filepath)

		return redirect(url_for('index'))
	else:
		return render_template('load.html')



@app.route('/finished', methods=['POST', 'GET'])
@rbac.allow(['professor'], ['POST', 'GET'])
def finished():
	# saves exam results
	# -----------------------

	if request.method == 'POST':
		username = str(request.form['username'])
		listnumber = int(request.form['listnumber'])
		ticketnumber = int(request.form['number'])
		grade = int(request.form['grade'])
		time = str(request.form['time'])

		TicketsAPI.results.append((username, listnumber, ticketnumber, grade, time))

		return redirect(url_for('index'))

	else:
		return render_template('finished.html')


@app.route('/history', methods=['POST', 'GET'])
@rbac.allow(['student', 'professor', 'admin'], ['GET', 'POST'])
def history(file=None):
	# print results
	# --------------------------
	if 'csv' in request.form:
		proxy = StringIO()
		writer = csv.writer(proxy, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		writer.writerows(TicketsAPI.results)

		mem = BytesIO()
		mem.write(proxy.getvalue().encode('utf-8'))
		mem.seek(0)
		proxy.close()

		return send_file(mem, attachment_filename='history.csv', as_attachment=True, mimetype='text/csv')

	if 'html' in request.form:
		return render_template('history.html', hist=TicketsAPI.results)

	return render_template('history_choose.html')


@app.route('/status')
@rbac.allow(['professor'], ['GET'])
def status():
	"""Shows given tickets."""
	history = tablehistorydef.get_history()
	return render_template('history.html', hist=history)


def checkUser(username, engine, dbName):
	# Checks if user in database

	Session = sessionmaker(bind=engine)
	session = Session()

	query = session.query(dbName).filter(dbName.username.in_([username]))
	result = query.first()

	return result


def getUserTickets(username):
	"""returns a list of tickets assigned for a user"""
	Session = sessionmaker(bind=tablehistorydef.history_engine)
	session = Session()
	tickets = session.query(tablehistorydef.Entry).filter(tablehistorydef.Entry.username.in_([username])).all()
	return tickets


def registerUser(username, role):

	Session = sessionmaker(bind=tableusersdef.users_engine)
	session = Session()
	user_role = tableusersdef.Role.get_by_name(role)
	user = tableusersdef.User(username, [user_role])
	local_user_object = session.merge(user)
	session.add(local_user_object)
	#session.add(user)
	session.commit()


def giveRandomTickets(username):

	Session = sessionmaker(bind=tablehistorydef.history_engine)
	session = Session()

	for ticket in TicketsAPI.getUserTickets():
		ticket.giveTo(username)
		number = ticket.getNumber()
		url = ticket.getUrl()

		entry = tablehistorydef.Entry(username, number, url)
		session.add(entry)

	session.commit()
