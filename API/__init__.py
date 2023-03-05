from flask import Flask
from flask_restx import Api
from .config.config import config_dict
from flask_jwt_extended import JWTManager
from .utils import db
from .auth.views import student_namespace as auth_namespace
from .courses.courses import course_namespace as course_namespace


def create_app(config=config_dict['dev']):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    jwt = JWTManager(app)
    authorizations = {
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Enter your Bearer Token'
        }
    }
    api = Api(app,
              title='Student Management System',
              version='1.0',
              description='A simple student management system',
              authorizations=authorizations,
              security='Bearer Auth',)

    api.add_namespace(auth_namespace, path='/auth')
    api.add_namespace(course_namespace, path='/course')
    return app
