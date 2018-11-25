from flask import redirect, render_template, request, session, url_for
from flask_login import login_user, current_user, logout_user


from project import rbac, db
from project.models import User, Role
from . import home_blueprint


@home_blueprint.route('/')
@rbac.exempt
def index():
    if session.get('logged_in'):
        return render_template('index.html', role=current_user.roles[0].name)
    else:
        return redirect(url_for('home.login'))


@home_blueprint.route('/login', methods=['POST', 'GET'])
@rbac.exempt
def login():
    if request.method == 'POST':
        username = str(request.form['username'])
        role = request.form.get('role')

        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username, roles=[Role.get_by_name(role)])

        user.authenticated = True
        session['logged_in'] = True
        session['username'] = username
        db.session.add(user)
        db.session.commit()
        login_user(user)

        return redirect(url_for('home.index'))
    else:
        return render_template('login.html')


@home_blueprint.route('/logout')
@rbac.exempt
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    session['logged_in'] = False
    session.pop('username', None)
    return redirect(url_for('home.index'))
