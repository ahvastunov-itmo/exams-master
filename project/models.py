from . import db
from flask_rbac import UserMixin, RoleMixin


users_roles = db.Table(
    'users_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)
    roles = db.relationship(
        'Role',
        secondary=users_roles,
        backref=db.backref('roles', lazy='dynamic')
    )

    def __init__(self, username, roles):
        self.username = username
        self.roles = roles
        self.authenticated = False

    @property
    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return self.authenticated

    def add_role(self, role):
        self.roles.append(role)

    def add_roles(self, roles):
        for role in roles:
            self.add_role(role)

    def get_roles(self):
        for role in self.roles:
            yield role

    def get_role(self):
        return self.roles[0].name


roles_parents = db.Table(
    'roles_parents',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('parent_id', db.Integer, db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    parents = db.relationship(
        'Role',
        secondary=roles_parents,
        primaryjoin=(id == roles_parents.c.role_id),
        secondaryjoin=(id == roles_parents.c.parent_id),
        backref=db.backref('children', lazy='dynamic')
    )

    def __init__(self, name):
        RoleMixin.__init__(self)
        self.name = name

    @staticmethod
    def get_by_name(name):
        return Role.query.filter_by(name=name).first()


class Entry(db.Model):
    __tablename__ = "entry"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    urls = db.Column(db.String)
    grade = db.Column(db.Integer)
    time = db.Column(db.Time)

    def __init__(self, username, urls):
        self.username = username
        self.urls = urls

    @staticmethod
    def get_history():
        entries = Entry.query.all()
        return [(entry.username, entry.urls,
                 entry.grade, entry.time) for entry in entries]
