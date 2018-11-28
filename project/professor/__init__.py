from flask import Blueprint

professor_blueprint = Blueprint(
    'professor',
    __name__,
    template_folder='templates',
    static_folder='static'
)

from . import views
