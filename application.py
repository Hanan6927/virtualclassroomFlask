import re
from flask import Flask, request, flash
from flask_marshmallow import Marshmallow
from flask_restplus import Api, Resource, fields
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from settings import *
from models import *
from ma import *



app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS


db.init_app(app)
ma = Marshmallow(app)

api = Api(app, version='1.0', title='Virtual Classroom API',
          description='A simple Virtual Classroom API')

StudentNamespace = api.namespace("Student", path="/api/student")
InstructorsNamespace = api.namespace("Instructor", path="/api/Instructor")


student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

course_schema = CourseSchema()
course_schema = CourseSchema(many=True)


# Model required by flask_restplus for expect
student = api.model("Students", {
    'FirstName': fields.String(),
    'LastName': fields.String(),
    'Email': fields.String(),
    'Password': fields.String(),
})

#############################################
'''
AUTHENTICATION
'''
#############################################

@api.route('/api/authenticate')
# @cross_origin()
class authentication(Resource):
    def get(self):
        return 

#############################################
'''
STUDENT
'''
#############################################

@StudentNamespace.route('/authenticate/students/createstudent')
class Student(Resource):
    @api.expect(student)
    def post(self):
        '''
        Create a new Student
        '''
        
        new_student = Students()
        new_student.FirstName = request.json['FirstName']
        new_student.LastName = request.json['LastName']
        new_student.Email = request.json['Email']
        new_student.Password = generate_password_hash(request.json['Password'], method='sha256')

        student = Students.query.filter_by(Email=new_student.Email).first()
        if student:
            return "Email already taken", 400

        db.session.add(new_student)
        db.session.commit()
        return student_schema.dump(new_student), 201

@api.route('/api/authenticate/students/<int:stuID>')
class studentResource(Resource):
    def get(self,stuID):
        '''
        Get Student Info
        '''
        student = Students.query.filter_by(StudentID=stuID).first()

        if student:
            return student_schema.dump(student)
        return "Student not found",404
    @api.expect
    def patch(self,stuID):
        '''
        Edit Student Info
        '''
        student = Students.query.filter_by(StudentID=stuID).first()

        return

@api.route('/api/authenticate/students/studentbyemail')
class studentsResources(Resource):
    def get(self):
        return

@api.route('/api/authenticate/students/studentbyemail/<int:studentEmail>')
class studentsResourcesOne(Resource):
    def get(self,studentEmail):
        return

#############################################
'''
INSTRUCTOR
'''
#############################################

@api.route('/api/authenticate/instructors')
class instructorsResource(Resource):
    def get(self):
        return

@api.route('/api/authenticate/instructors/createinstructor')
class instructorsResource(Resource):
    def post(self):
        return 


@api.route('/api/authenticate/instructors/<int:instructorID>')
class instructorResource(Resource):
    def get(self,instructorID):
        return
    
    def patch(self,instructorID):
        return

#############################################
'''
RESOURCE
'''
#############################################
@api.route('/api/courses/<int:courseID>/Resources')
class resourcesResource(Resource):
    def get(self,courseID):
        return

    def post(self,courseID):
        return

@api.route('/api/courses/<int:courseID>/resources/<int:resourceID>')
class resourceResource(Resource):
    def get(self,courseID,resourceID):
        return
    
    def delete(self,courseID,resourceID):
        return

@api.route('/api/courses/<int:courseID>/resources/<int:resourceID>/download')
class resourcesResourceOne(Resource):
    def get(self,courseID,resourceID):
        return

#############################################
'''
COURSE
'''
#############################################
@api.route('/api/courses')
class coursesResource(Resource):
    def post(self):
        return

@api.route('/api/courses/<int:courseID>')
class courseResource(Resource):
    def get(self,courseID):
        return
    
    def post(self,courseID):
        return
    
    def patch(self,courseID):
        return

@api.route('/api/courses/<int:courseID>/student/<int:ids>')
class courseResourceOne(Resource):
    def get(self,courseID,ids):
        return
    
@api.route('/api/courses/<int:courseID>/students')
class courseResourceTwo(Resource):
    def get(self,courseID):
        return

@api.route('/api/courses/studentcourses')
class courseResourceThree(Resource):
    def get(self):
        return

@api.route('/api/courses/studentcourses/<int:courseID>')
class courseResourceFour(Resource):
    def get(self,courseID):
        return

@api.route('/api/courses/instructorcourses')
class courseResourceFive(Resource):
    def get(self):
        return
    
#############################################
'''
CLASSROOM
'''
#############################################

@api.route('/api/courses/<int:courseID>/classrooms/<int:classroomID>')
class classroomResource(Resource):
    def get(self,courseID,classroomID):
        return
    
    def patch(self,courseID,classroomID):
        return

@api.route('/api/courses/<int:courseID>/classrooms')
class classroomResourceOne(Resource):
    def get(self,courseID):
        return
    
    def post(self,courseID):
        return
    
@api.route('/api/courses/<int:courseID>/classrooms/<int:classroomID>/join')
class classroomResourceTwo(Resource):
    def get(self,courseID,classroomID):
        return

if __name__ == "__main__":
    app.run(debug=True)