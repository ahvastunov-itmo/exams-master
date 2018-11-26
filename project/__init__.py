from flask import Flask, session
from flask_rbac import RBAC
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user


db = SQLAlchemy()
rbac = RBAC()
login = LoginManager()
login.login_view = 'home.login'


def create_app(config_filename=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(config_filename)
    initialize_extensions(app)
    register_blueprints(app)
    return app


def initialize_extensions(app):
    db.init_app(app)
    rbac.init_app(app)
    login.init_app(app)

    from project.models import User, Role, Entry

    with app.test_request_context():
        db.create_all()

        for role_name in ['anonymous', 'student', 'professor', 'admin']:
            if not Role.query.filter_by(name=role_name).first():
                role = Role(role_name)
                db.session.add(role)

        db.session.commit()

    rbac.set_user_model(User)
    rbac.set_role_model(Role)

    @login.user_loader
    def load_user(user_id):
        return User.query.filter(User.id == int(user_id)).first()

    def get_current_user():
        if session.get('logged_in'):
            return User.query.filter_by(
                username=session.get('username')).first()
        else:
            return User('anon', roles=[Role.get_by_name('anonymous')])

    rbac.set_user_loader(get_current_user)


def register_blueprints(app):
    from project.admin import admin_blueprint
    from project.home import home_blueprint
    from project.professor import professor_blueprint
    from project.student import student_blueprint

    app.register_blueprint(admin_blueprint)
    app.register_blueprint(home_blueprint)
    app.register_blueprint(professor_blueprint)
    app.register_blueprint(student_blueprint)
