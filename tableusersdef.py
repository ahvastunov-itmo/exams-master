from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_rbac import UserMixin, RoleMixin
#from tablerolesdef import Role

users_engine = create_engine('sqlite:///users.db', echo=True)
role_engine = create_engine('sqlite:///role.db', echo=True)
Base = declarative_base()


users_roles = Table(
	'users_roles',
	Base.metadata,
	Column('user_id', Integer, ForeignKey('user.id')),
	Column('role_id', Integer, ForeignKey('role.id'))
)


class User(Base, UserMixin):
	__tablename__ = "user"

	id = Column(Integer, primary_key=True)
	username = Column(String)
	roles = relationship(
		'Role',
		secondary=users_roles,
		backref='roles'
	)


	def __init__(self, username, roles):
		self.username = username
		self.roles = roles


	def add_role(self, role):
		self.roles.append(role)


	def add_roles(self, roles):
		for role in roles:
			self.add_role(role)


	def get_roles(self):
		for role in self.roles:
			yield role


roles_parents = Table(
	'roles_parents',
	Base.metadata,
	Column('role_id', Integer, ForeignKey('role.id')),
	Column('parent_id', Integer, ForeignKey('role.id'))
)


class Role(Base, RoleMixin):
	__tablename__ = "role"

	id = Column(Integer, primary_key=True)
	name = Column(String)
	parents = relationship(
		'Role',
		secondary = roles_parents,
		primaryjoin = (id == roles_parents.c.role_id),
		secondaryjoin = (id == roles_parents.c.parent_id),
		backref = 'children'
	)


	def __init__(self, name):
		RoleMixin.__init__(self)
		self.name = name


	@staticmethod
	def get_by_name(name):
		Session = sessionmaker(bind=role_engine)
		session = Session()
		query = session.query(Role).filter(Role.name.in_([name]))
		return query.first()


# create tables
Base.metadata.create_all(users_engine)

if role_engine.dialect.has_table(role_engine, 'Role'):
	Role.__table__.drop(role_engine)
Base.metadata.create_all(role_engine)

Session = sessionmaker(bind=role_engine)
session = Session()
session.add(Role('anonymous'))
session.add(Role('student'))
session.add(Role('professor'))
session.add(Role('admin'))
session.commit()