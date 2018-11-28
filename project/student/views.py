from flask import (redirect, render_template, request, session, url_for,
                   current_app)
from flask_login import current_user

from project.tickets import TicketsAPI
from project import rbac, db
from project.models import Entry
from . import student_blueprint


@student_blueprint.route('/random')
@rbac.allow(['student', 'admin'], ['GET'])
def random():
    if not session.get('logged_in'):
        return redirect(url_for('home.login'))
    else:
        if not TicketsAPI.ticketsLoaded():
            current_app.logger.warning('No tickets loaded')
            return redirect(url_for('home.index'))
        # check if we already gave random number to this student
        username = session.get('username')
        result = Entry.query.filter_by(username=username).first()
        if not result:
            for ticket in TicketsAPI.getUserTickets():
                ticket.giveTo(username)
                number = ticket.getNumber()
                url = ticket.getUrl()
                db.session.add(Entry(username, number, url))
            db.session.commit()

        tickets = Entry.query.filter_by(username=username).all()
        return render_template('random.html', tickets=tickets)
