from flask import (redirect, render_template, request, url_for, send_file,
                   current_app)
from io import StringIO, BytesIO
import csv


from project.tickets import TicketsAPI
from project import rbac
from project.models import Entry
from . import professor_blueprint


@professor_blueprint.route('/load', methods=['POST', 'GET'])
@rbac.allow(['professor', 'admin'], ['POST', 'GET'])
def load():
    # loads ticket lists from uploaded json file
    if request.method == 'POST':
        if 'file' not in request.files:
            current_app.logger.warning('No file part')
            return redirect(request.url)
        file = request.files['file']
        if not file.filename:
            current_app.logger.warning('No selected file')
            return redirect(request.url)

        filepath = str(current_app.config['JSON_PATH'])
        file.save(filepath)

        TicketsAPI.loadTickets(filepath)

        return redirect(url_for('home.index'))
    else:
        return render_template('load.html')


@professor_blueprint.route('/finished', methods=['POST', 'GET'])
@rbac.allow(['professor', 'admin'], ['POST', 'GET'])
def finished():
    # saves exam results
    if request.method == 'POST':
        username = str(request.form['username'])
        listnumber = int(request.form['listnumber'])
        ticketnumber = int(request.form['number'])
        grade = int(request.form['grade'])
        time = str(request.form['time'])

        TicketsAPI.results.append(
            (username, listnumber, ticketnumber, grade, time))

        return redirect(url_for('home.index'))

    else:
        return render_template('finished.html')


@professor_blueprint.route('/history', methods=['POST', 'GET'])
@rbac.allow(['student', 'professor', 'admin'], ['GET', 'POST'])
def history(file=None):
    # print results
    if 'csv' in request.form:
        proxy = StringIO()
        writer = csv.writer(
            proxy, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(TicketsAPI.results)

        mem = BytesIO()
        mem.write(proxy.getvalue().encode('utf-8'))
        mem.seek(0)
        proxy.close()

        return send_file(
            mem,
            attachment_filename='history.csv',
            as_attachment=True,
            mimetype='text/csv')

    if 'html' in request.form:
        return render_template('history.html', hist=TicketsAPI.results)

    return render_template('history_choose.html')


@professor_blueprint.route('/status')
@rbac.allow(['professor', 'admin'], ['GET'])
def status():
    """Shows given tickets."""
    history = Entry.get_history()
    return render_template('history.html', hist=history)
