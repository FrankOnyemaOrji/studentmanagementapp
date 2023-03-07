from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields
from ..utils import db
from ..models.student import UserModel
from ..models.course import CourseModel

from http import HTTPStatus
from flask import request

course_namespace = Namespace('course', description='coursename')

CourseModel = course_namespace.model(
    'CourseRegistration', {
        'id': fields.Integer(required=True, description='ID of the course'),
        'name': fields.String(required=True, description='Name of the course'),
        'teacher': fields.String(required=True, description='Teacher of the course'),
    }
)

GradeModel = course_namespace.model(
    'Grades', {
        'id': fields.Integer(required=True, description='ID of the course'),
        'registration_id': fields.Integer(required=True, description='ID of the registration'),
        'grade': fields.Integer(required=True, description='Grade of the student'),
        'date': fields.DateTime(required=True, description='Date of the grade'),
    }
)


@course_namespace.route('/courses')
class Courses(Resource):
    @course_namespace.marshal_list_with(CourseModel)
    @jwt_required
    def get(self):
        """Get all courses"""
        course = CourseModel.query.all()
        if not course:
            return {'message': 'No courses found'}, HTTPStatus.NOT_FOUND
        current_user_id = get_jwt_identity()
        current_user = UserModel.get_by_id(current_user_id)
        if not current_user.is_admin or not current_user.name:
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED
        return course, HTTPStatus.OK

    @course_namespace.expect(CourseModel)
    @course_namespace.marshal_with(CourseModel)
    @jwt_required
    def post(self):
        """Create a course"""
        data = request.get_json()
        course = CourseModel(name=data.get(
            'name'), teacher=data.get('teacher'))
        current_user_id = get_jwt_identity()
        current_user = UserModel.get_by_id(current_user_id)
        if not current_user.is_admin:
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED
        course.save()
        return course, HTTPStatus.CREATED

    def course_dict(self, course):
        return {
            'id': course.id,
            'name': course.name,
            'teacher': course.teacher,
            'students': [student.serialize() for student in course.students]
        }


@course_namespace.route('/courses/<int:id>')
class Course(Resource):
    @course_namespace.marshal_with(CourseModel)
    @jwt_required
    def get(self, id):
        """Get a course"""
        course = CourseModel.query.filter_by(id=id).first()
        if not course:
            return {'message': 'course not found'}, HTTPStatus.NOT_FOUND
        curerent_user_id = get_jwt_identity()
        current_user = UserModel.get_by_id(curerent_user_id)
        if not current_user.is_admin or not current_user.name:
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED
        return course, HTTPStatus.OK

    @course_namespace.marshal_with(CourseModel)
    @course_namespace.expect(CourseModel)
    @jwt_required
    def put(self, id):
        """Update a course"""
        course = CourseModel.query.filter_by(id=id).first()
        if not course:
            return {'message': 'course not found'}, HTTPStatus.NOT_FOUND
        data = request.get_json()
        current_user_id = get_jwt_identity()
        current_user = UserModel.get_by_id(current_user_id)
        if not current_user.is_admin:
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED
        course.name = data.get('name')
        course.teacher = data.get('teacher')
        course.save()
        return course, HTTPStatus.OK

    def delete(self, id):
        """Delete a course"""
        course = CourseModel.query.filter_by(id=id).first()
        if not course:
            return {'message': 'course not found'}, HTTPStatus.NOT_FOUND
        current_user_id = get_jwt_identity()
        current_user = UserModel.get_by_id(current_user_id)
        if not current_user.is_admin:
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED
        course.delete()
        return {'message': 'course deleted'}, HTTPStatus.OK

    def course_dict(self, course):
        return {
            'id': course.id,
            'name': course.name,
            'teacher': course.teacher,
            'students': [student.serialize() for student in course.students]
        }


@course_namespace.route('/courses/<int:id>/students')
@course_namespace.param('id', 'The course identifier')
class CourseStudents(Resource):
    @course_namespace.marshal_with(CourseModel)
    @jwt_required
    def get(self, id):
        """Get all students in a course"""
        course = CourseModel.query.filter_by(id=id).first()
        if not course:
            return {'message': 'course not found'}, HTTPStatus.NOT_FOUND
        current_user_id = get_jwt_identity()
        current_user = UserModel.get_by_id(current_user_id)
        if not current_user.is_admin:
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED
        return course, HTTPStatus.OK


@course_namespace.route('/grades')
class Grades(Resource):
    @course_namespace.marshal_list_with(CourseModel)
    @jwt_required
    def get(self):
        """Get all grades"""
        grade = CourseModel.query.all()
        if not grade:
            return {'message': 'No grades found'}, HTTPStatus.NOT_FOUND
        current_user_id = get_jwt_identity()
        current_user = UserModel.get_by_id(current_user_id)
        if not current_user.is_admin or not current_user.name:
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED
        return grade, HTTPStatus.OK

    @course_namespace.expect(CourseModel)
    @course_namespace.marshal_with(CourseModel)
    @jwt_required
    def post(self):
        """Create a grade"""
        data = request.get_json()
        course = CourseModel.query.filter_by(id=data.get('course_id')).first()
        if not course:
            return {'message': 'course not found'}, HTTPStatus.NOT_FOUND
        current_user_id = get_jwt_identity()
        current_user = UserModel.get_by_id(current_user_id)
        if not current_user.is_admin:
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED
        grade = CourseModel(registration_id=data.get(
            'registration_id'), grade=data.get('grade'), date=data.get('date'))
        grade.save()
        return grade, HTTPStatus.CREATED

    def grade_dict(self, grade):
        return {
            'id': grade.id,
            'registration_id': grade.registration_id,
            'grade': grade.grade,
            'date': grade.date,
        }


@course_namespace.route('/gpa/<int:id>')
@course_namespace.param('id', 'The student identifier')
class GPA(Resource):
    @course_namespace.marshal_with(CourseModel)
    @jwt_required
    def get(self, id):
        """Get GPA"""
        current_user_id = get_jwt_identity()
        current_user = UserModel.get_by_id(current_user_id)
        if not current_user.is_admin:
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED
        grades = GradeModel.query.filter_by(student_id=id).all()
        if not grades:
            return {'gpa': 0.0}, HTTPStatus.OK
        total_gpa_points = 0.0
        total_grades = 0
        for grade in grades:
            course = CourseModel.query.filter_by(id=grade.course_id).first()
            total_gpa_points += grade.grade * course.credit
            total_grades += course.credit
        gpa = total_gpa_points / total_grades
        return {'gpa': gpa}, HTTPStatus.OK
