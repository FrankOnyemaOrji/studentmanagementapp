import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from ..models.student import StudentModel
from flask_jwt_extended import create_access_token


class TestStudentAuth(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_dict['test'])
        self.client = self.app.test_client()
        self.appctx = self.app.app_context()
        self.appctx.push()
        db.create_all()


    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_students(self):
        # add some test students to the database
        student1 = StudentModel(name='John Doe', id=1, email='john@example.com')
        student2 = StudentModel(name='Jane Doe', id=2, email='jane@example.com')
        db.session.add_all([student1, student2])
        db.session.commit()

        # send a GET request to the /students endpoint with a valid access token
        access_token = create_access_token(identity=1)
        response = self.client.get('/students', headers={'Authorization': f'Bearer {access_token}'})

        # check that the response is valid
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['name'], 'John Doe')
        self.assertEqual(response.json[1]['email'], 'jane@example.com')