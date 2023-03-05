from flask_restx import Namespace, Resource, fields
from ..utils import db
from ..models.student import StudentModel
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
    def get(self):
        """Get all courses"""
        return CourseModel.query.all()
    
    @course_namespace.expect(CourseModel)
    @course_namespace.marshal_with(CourseModel)
    def post(self):
        """Create a course"""
        data = request.get_json()
        course = CourseModel(name=data.get('name'),teacher=data.get('teacher'))
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
    def get(self, id):
        """Get a course"""
        course = CourseModel.query.filter_by(id=id).first()
        if not course:
            return {'message': 'course not found'}, HTTPStatus.NOT_FOUND
        return course, HTTPStatus.OK
    
    @course_namespace.marshal_with(CourseModel)
    @course_namespace.expect(CourseModel)
    def put(self, id):
        """Update a course"""
        course = CourseModel.query.filter_by(id=id).first()
        if not course:
            return {'message': 'course not found'}, HTTPStatus.NOT_FOUND
        data = request.get_json()
        course.name = data.get('name')
        course.teacher = data.get('teacher')
        course.save()
        return course, HTTPStatus.OK
    
    def delete(self, id):
        """Delete a course"""
        course = CourseModel.query.filter_by(id=id).first()
        if not course:
            return {'message': 'course not found'}, HTTPStatus.NOT_FOUND
        course.delete()
        return '', HTTPStatus.NO_CONTENT
    
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
    def get(self, id):
        """Get all students in a course"""
        course = CourseModel.query.filter_by(id=id).first()
        if not course:
            return {'message': 'course not found'}, HTTPStatus.NOT_FOUND
        return course, HTTPStatus.OK
    

@course_namespace.route('/grades')
class Grades(Resource):
    @course_namespace.marshal_list_with(CourseModel)
    def get(self):
        """Get all grades"""
        grade = CourseModel.query.all()
        return grade, HTTPStatus.OK
    
    @course_namespace.expect(CourseModel)
    @course_namespace.marshal_with(CourseModel)
    def post(self):
        """Create a grade"""
        data = request.get_json()
        student = StudentModel.query.filter_by(id=data.get('student_id')).first()
        if not student:
            return {'message': 'student not found'}, HTTPStatus.NOT_FOUND
        course = CourseModel.query.filter_by(id=data.get('course_id')).first()
        if not course:
            return {'message': 'course not found'}, HTTPStatus.NOT_FOUND
        grade = CourseModel(registration_id=data.get('registration_id'),grade=data.get('grade'),date=data.get('date'))
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
    def get(self, id):
        """Get GPA"""
        student = StudentModel.query.filter_by(id=id).first()
        if not student:
            return {'message': 'student not found'}, HTTPStatus.NOT_FOUND
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