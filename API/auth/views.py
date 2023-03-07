from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields
from werkzeug.security import check_password_hash, generate_password_hash
from ..utils import db
from ..models.student import UserModel
from http import HTTPStatus
from flask import request


student_namespace = Namespace('auth', description='Authentication')

auth_model = student_namespace.model(
    'StudentRegistration', {
        'student_id': fields.Integer(required=True, description='ID of the student'),
        'course_id': fields.Integer(required=True, description='ID of the course'),
    }
)

UserModel = student_namespace.model(
    'Student', {
        'id': fields.Integer(required=True, description='ID of the student'),
        'name': fields.String(required=True, description='Name of the student'),
        'email': fields.String(required=True, description='Email of the student'),
        'role': fields.String(required=True, description='Role of the student'),
    }
)



login_model = student_namespace.model(
    'Login', {
        'email': fields.String(required=True, description='Email of the student'),
        'password': fields.String(required=True, description='Password of the student'),
    }
)

@student_namespace.route('/students')
class Students(Resource):
    @student_namespace.marshal_list_with(UserModel)
    @jwt_required
    def get(self):
        """Get all students"""
        current_user_id = get_jwt_identity()
        current_user = UserModel.get_by_id(current_user_id)
        if not current_user.is_admin:
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED
    
    @student_namespace.expect(auth_model)
    @student_namespace.marshal_with(UserModel)
    def post(self):
        """Create a student"""
        data = request.get_json()
        student = UserModel(username=data.get('username'),email=data.get('email'),password=generate_password_hash(data.get('password')))
        student.save()
        return student, HTTPStatus.CREATED
    
    def student_dict(self, student):
        return {
            'id': student.id,
            'name': student.name,
            'email': student.email,
            'courses': [course.serialize() for course in student.courses]
        }
    
@student_namespace.route('/students/<int:id>')
class Student(Resource):
    @student_namespace.marshal_with(UserModel)
    @jwt_required
    def get(self, id):
        """Get a student"""
        student = UserModel.get_by_id(id)
        if not student:
            return {'message': 'Student not found'}, HTTPStatus.NOT_FOUND
        
        current_user_id = get_jwt_identity()
        current_user = UserModel.get_by_id(current_user_id)

        if not current_user.is_admin:
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED
        return student, HTTPStatus.OK
    
    @student_namespace.expect(UserModel)
    @student_namespace.marshal_with(UserModel)
    def put(self, id):
        """Update a student"""
        data = request.get_json()
        student = UserModel.query.filter_by(id=id).first()
        if not Student:
            return {'message': 'Student not found'}, HTTPStatus.NOT_FOUND
        
        current_user_id = get_jwt_identity()
        current_user = UserModel.get_by_id(current_user_id)

        if not current_user.is_admin:
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED
        
        student.username = data.get('username')
        student.email = data.get('email')
        student.save()
        return student, HTTPStatus.OK
    
    def delete(self, id):
        """Delete a student"""
        student = UserModel.query.filter_by(id=id).first()
        if not student:
            return {'message': 'Student not found'}, HTTPStatus.NOT_FOUND
        
        current_user_id = get_jwt_identity()
        current_user = UserModel.get_by_id(current_user_id)

        if not current_user.is_admin:
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED

        student.delete()
        return {'message': 'Student delected successfully'}, HTTPStatus.NO_CONTENT



@student_namespace.route('/signup')
class SignUp(Resource):
    """Sign up a student"""
    @student_namespace.expect(auth_model)
    @student_namespace.marshal_with(UserModel)
    def post(self):
        data = request.get_json()
        if data['role'] not in ['admin', 'student']:
            return {'message': 'Invalid role'}, HTTPStatus.BAD_REQUEST
        if data['role'] == 'admin':
            new_user = UserModel(username=data.get('username'),email=data.get('email'),password=generate_password_hash(data.get('password')), is_admin=True)
        else:
            new_user = UserModel(username=data.get('username'),email=data.get('email'),password=generate_password_hash(data.get('password')), is_admin=False)
        new_user.save()
        return new_user, HTTPStatus.CREATED

@student_namespace.route('/login')
class Login(Resource):
    @student_namespace.expect(login_model)
    def post(self):
        """Login a student"""
        data = request.get_json()
        if not data:
            return {'message': 'No input data provided'}, HTTPStatus.BAD_REQUEST
        
        if data['role'] not in ['admin', 'student']:
            return {'message': 'Invalid role'}, HTTPStatus.BAD_REQUEST
        user = UserModel.get_by_email(data.get('email'))
        if not user:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND
        if not check_password_hash(user.password, data.get('password')):
            return {'message': 'Wrong credentials'}, HTTPStatus.UNAUTHORIZED
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            }

@student_namespace.route('/refresh')
class Refresh(Resource):
    """Refresh access token"""
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}, HTTPStatus.OK