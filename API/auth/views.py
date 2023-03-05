from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields
from werkzeug.security import check_password_hash, generate_password_hash
from ..utils import db
from ..models.student import StudentModel
from http import HTTPStatus
from flask import request


student_namespace = Namespace('auth', description='Authentication')

auth_model = student_namespace.model(
    'StudentRegistration', {
        'student_id': fields.Integer(required=True, description='ID of the student'),
        'course_id': fields.Integer(required=True, description='ID of the course'),
    }
)

StudentModel = student_namespace.model(
    'Student', {
        'id': fields.Integer(required=True, description='ID of the student'),
        'username': fields.String(required=True, description='Name of the student'),
        'email': fields.String(required=True, description='Email of the student'),
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
    @student_namespace.marshal_list_with(StudentModel)
    def get(self):
        """Get all students"""
        return StudentModel.query.all()
    
    @student_namespace.expect(auth_model)
    @student_namespace.marshal_with(StudentModel)
    def post(self):
        """Create a student"""
        data = request.get_json()
        student = StudentModel(username=data.get('username'),email=data.get('email'),password=generate_password_hash(data.get('password')))
        student.save()
        return student, HTTPStatus.CREATED
    
    def student_dict(self, student):
        return {
            'id': student.id,
            'username': student.username,
            'email': student.email,
            'courses': [course.serialize() for course in student.courses]
        }
    
@student_namespace.route('/students/<int:id>')
class Student(Resource):
    @student_namespace.marshal_with(StudentModel)
    def get(self, id):
        """Get a student"""
        student = StudentModel.get_by_id(id)
        if not student:
            return {'message': 'Student not found'}, HTTPStatus.NOT_FOUND
        return student, HTTPStatus.OK
    
    @student_namespace.expect(StudentModel)
    @student_namespace.marshal_with(StudentModel)
    def put(self, id):
        """Update a student"""
        data = request.get_json()
        student = StudentModel.query.filter_by(id=id).first()
        if not Student:
            return {'message': 'Student not found'}, HTTPStatus.NOT_FOUND
        student.username = data.get('username')
        student.email = data.get('email')
        student.save()
        return student, HTTPStatus.OK
    
    def delete(self, id):
        """Delete a student"""
        student = StudentModel.query.filter_by(id=id).first()
        if not student:
            return {'message': 'Student not found'}, HTTPStatus.NOT_FOUND
        student.delete()
        return '', HTTPStatus.NO_CONTENT



@student_namespace.route('/signup')
class SignUp(Resource):
    @student_namespace.expect(auth_model)
    @student_namespace.marshal_with(StudentModel)
    def post(self):
        data = request.get_json()
        student = StudentModel(username=data.get('username'),password=generate_password_hash(data.get('password')))
        student.save()
        return student, HTTPStatus.CREATED
    
    def student_dict(self, student):
        return {
            'id': student.id,
            'username': student.username,
        }

@student_namespace.route('/login')
class Login(Resource):
    @student_namespace.expect(login_model)
    def post(self):
        """Login a student"""
        data = request.get_json()
        student = StudentModel.query.filter_by(email=data.get('email')).first()
        if not student or not check_password_hash(student.password, data.get('password')):
            return {'message': 'Invalid credentials'}, HTTPStatus.UNAUTHORIZED
        access_token = create_access_token(identity=student.id)
        refresh_token = create_refresh_token(identity=student.id)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            }
    
@student_namespace.route('/students')
class Students(Resource):
    @jwt_required()
    @student_namespace.marshal_list_with(StudentModel)
    def get(self):
        """Get all students"""
        students = StudentModel.query.all()
        return students, HTTPStatus.OK
    
    def student_dict(self, student):
        return {
            'id': student.id,
            'username': student.username,
        }


@student_namespace.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}, HTTPStatus.OK