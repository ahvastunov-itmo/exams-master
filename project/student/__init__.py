from flask import Blueprint

student_blueprint = Blueprint(
    'student',
    __name__,
    template_folder='templates',
    static_folder='static'
)

from . import views
