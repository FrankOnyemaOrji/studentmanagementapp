from ..utils import db
from datetime import datetime


class StudentModel(db.Model):
    __tablename__ = 'student'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    courses = db.relationship('CourseModel', secondary='registrations', backref='students')

    def __repr__(self) -> str:
        return f"<Student {self.id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def serialize(self):
        return {
            'id': self.id,
            'username': self.name,
            'email': self.email,
            'courses': [course.serialize() for course in self.course]
        }

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)
    

class GradeModel(db.Model):
    __tablename__ = 'grade'

    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Float, nullable=False)
    registration_id = db.Column(db.Integer, db.ForeignKey('registrations.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Grade {self.id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def serialize(self):
        return {
            'id': self.id,
            'grade': self.grade,
            'student_id': self.student_id,
            'course_id': self.course_id
        }

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)