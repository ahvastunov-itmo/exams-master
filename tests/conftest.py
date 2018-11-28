import pytest
from project import create_app, db
from project.models import User, Role


@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('flask_test.cfg')

    testing_client = flask_app.test_client()

    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()


@pytest.fixture(scope='module')
def init_database():
    db.create_all()

    for role_name in ['anonymous', 'student', 'professor', 'admin']:
        role = Role(role_name)
        db.session.add(role)

    db.session.commit()

    student1 = User('Petya', roles=[Role.get_by_name('student')])
    student2 = User('Vasya', roles=[Role.get_by_name('student')])
    professor = User('teacher', roles=[Role.get_by_name('professor')])
    admin = User('root', roles=[Role.get_by_name('admin')])

    db.session.add(student1)
    db.session.add(student2)
    db.session.add(professor)
    db.session.add(admin)

    db.session.commit()

    yield db

    db.drop_all()
