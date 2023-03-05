from ..utils import db


class Registration(db.Model):
    __tablename__ = 'registrations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_model.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course_model.id'), primary_key=True)
    grade = db.relationship('GradeModel', backref='registration', lazy=True)
    
    def __repr__(self) -> str:
        return f"<StudentCourse {self.id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)