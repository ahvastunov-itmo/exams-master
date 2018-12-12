from flask import (redirect, render_template, session, url_for,
                   current_app, flash)

from project.tickets import TicketsAPI
from project import rbac, db
from project.models import Entry
from . import student_blueprint


@student_blueprint.route('/')
@rbac.allow(['student', 'admin'], ['GET'])
def index():
    return render_template('student.html')


@student_blueprint.route('/random')
@rbac.allow(['student', 'admin'], ['GET'])
def random():
    if not session.get('logged_in'):
        return redirect(url_for('home.login'))
    else:
        if not TicketsAPI.ticketsLoaded():
            current_app.logger.warning('No tickets loaded')
            flash('No tickets loaded yet!')
            return redirect(url_for('student.index'))
        # check if we already gave random number to this student
        username = session.get('username')
        result = Entry.query.filter_by(username=username).first()
        if not result:
            urls = ','.join(
                [ticket.getUrl() for ticket in TicketsAPI.getUserTickets()]
            )
            db.session.add(Entry(username, urls))
            db.session.commit()

        entry = Entry.query.filter_by(username=username).first()
        return render_template('random.html', entry=entry)
