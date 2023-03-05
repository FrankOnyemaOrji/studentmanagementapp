Student Management App

The Student Management App is a RESTful API that allows users to manage students and courses.

API Endpoints
Students
POST /students: Create a new student. The request body should include a JSON object with the following properties:

name (string): The name of the student.
id (string): The ID of the student.
email (string): The email address of the student.
Example Request Body: {"name": "John Doe", "id": "12345", "email": "john.doe@example.com"}
Example Response: 201 Created
GET /students: Get a list of all students.

Example Response: 200 OK
GET /students/{id}: Get information about a specific student with the given ID.

Example Response: 200 OK
PUT /students/{id}: Update information about a specific student with the given ID. The request body should include a JSON object with the properties to update.

Example Request Body: {"email": "john.doe@newemail.com"}
Example Response: 200 OK
DELETE /students/{id}: Delete a specific student with the given ID.

Example Response: 204 No Content
Courses
POST /courses: Create a new course. The request body should include a JSON object with the following properties:

name (string): The name of the course.
id (string): The ID of the course.
teacher (string): The name of the teacher of the course.
students (list): A list of student IDs enrolled in the course.
Example Request Body: {"name": "Math 101", "id": "MATH101", "teacher": "Jane Smith", "students": ["12345", "67890"]}
Example Response: 201 Created
GET /courses: Get a list of all courses.

Example Response: 200 OK
GET /courses/{id}: Get information about a specific course with the given ID.

Example Response: 200 OK
PUT /courses/{id}: Update information about a specific course with the given ID. The request body should include a JSON object with the properties to update.

Example Request Body: {"teacher": "John Doe", "students": ["12345", "67890", "11111"]}
Example Response: 200 OK
DELETE /courses/{id}: Delete a specific course with the given ID.

Example Response: 204 No Content
Grades
POST /grades: Create a new grade for a specific student and course. The request body should include a JSON object with the following properties:

student_id (string): The ID of the student.
course_id (string): The ID of the course.
grade (float): The grade for the student in the course.
Example Request Body: {"student_id": "12345", "course_id": "MATH101", "grade": 3.5}
Example Response: 201 Created
GET /grades: Get a list of all grades.

Example Response: 200 OK
GET /grades/{student_id}/{course_id}: Get the grade for a specific student and course.

Example Response: 200 OK

Authentication and Authorization
The API uses JWT tokens for authentication and authorization. Users must register and log in to access the protected endpoints.

Registration
To register as a new user, send a POST request to http://localhost:5000/api/v1/auth/register with the following fields in the request body:

username: a unique username
email: a valid email address
password: a strong password

Login

To log in to the API, send a POST request to http://localhost:5000/api/v1/auth/login with the following fields in the request body:

username: the username used during registration
password: the password used during registration

Testing:

To test the application, you can use Python's built-in unittest module or a third-party library like pytest. The testing framework should be specified in the requirements.txt file so that others can install the dependencies needed for testing.

The following are the steps to test the Student Management App using the pytest framework:

Install the required dependencies: pytest, pytest-flask, and coverage. You can install these dependencies using pip by running the following command:

*pip install pytest pytest-flask coverage*

And run the command:
*python -m unittest discover -s test*
to test the application