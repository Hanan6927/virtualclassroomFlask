import re
import os
import uuid
import datetime
from flask import Flask, request, flash, make_response
from flask_marshmallow import Marshmallow
from flask_restplus import Api, Resource, fields,reqparse
from flask_cors import CORS
from marshmallow import ValidationError
from flask_jwt_extended import (get_jwt_identity)


from werkzeug.security import generate_password_hash, check_password_hash

from settings import *
from models import *
from ma import *
import json
from flask_jwt_extended import JWTManager
from flask_jwt_extended import ( create_access_token, get_jwt,
                            jwt_required, get_jwt_identity)
from datetime import timedelta
import datetime
from datetime import datetime


app = Flask(__name__)
CORS(app)
jwt=JWTManager(app)
db_uri = SQLALCHEMY_DATABASE_URI
upload_folder = UPLOAD_FOLDER

if db_uri.startswith("postgres://"):
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['JWT_SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['JWT_BLACKLIST_ENABLED'] = ['access']
app.debug = True

db.init_app(app)
ma = Marshmallow(app)

api = Api(app, version='1.0', title='Virtual Classroom API',
          description='A simple Virtual Classroom API')

AuthenticationNamespace = api.namespace("Authentication", path="/api/authenticate")
StudentNamespace = api.namespace("Student", path="/api/authenticate/students")
InstructorsNamespace = api.namespace("Instructor", path="/api/authenticate/instructors")
ClassroomNamspace = api.namespace("Classroom", path="/api/courses")
ResourceNamespace = api.namespace("Resource", path="/api/course")
CourseNamespace = api.namespace("Course", path="/api/courses")


student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

instructor_schema = InstructorSchema()
instructors_schema = InstructorSchema(many=True)

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)

add_student_schema = AddStudentSchema()
add_students_schema = AddStudentSchema(many=True)

classroom_schema = ClassroomSchema()
classrooms_schema = ClassroomSchema(many=True)

studentList_schema = StudentListSchema(many=True)

resource_schema = ResourceSchema()


# Model required by flask_restplus for expect
student = api.model("Students", {
    'FirstName': fields.String(),
    'LastName': fields.String(),
    'Email': fields.String(),
    'Password': fields.String(),
})


# Model required by flask_restplus for expect
course = api.model("Courses", {
    'InstructorID': fields.Integer(),
    'CourseTitle': fields.String(),
    'CourseDescription': fields.String(),
    
})


courseStudents = api.model("CourseStudents",{
    'CourseID': fields.Integer(),
    'StudentID': fields.Integer()
})


instructor = api.model("Instructors", {
    'FirstName': fields.String(),
    'LastName': fields.String(),
    'Email': fields.String(),
    'Password': fields.String(),
})

classroom = api.model("Virtualclassrooms",{
    'ClassroomName': fields.String(),
    'Date': fields.String(),
    'StartTime': fields.String(),
    'EndTime': fields.String()
})

#############################################
'''
AUTHENTICATION
'''
#############################################

AuthenticationNamespace = api.namespace("Authentication", path="/api/authenticate")

user_auth_arguments = reqparse.RequestParser()
user_auth_arguments.add_argument('username', type=str, help="Username", required=True)
user_auth_arguments.add_argument('password', type=str, help="Password", required=True)

userCred = api.model("UserCred", {
    'UserName': fields.String(),
    'Password': fields.String() 
})

@AuthenticationNamespace.route('')
# @cross_origin()

class authentication(Resource):
    @api.expect(userCred)
    def post(self):
        print("\n\n\nhere\n\n\n")
        # args = user_auth_arguments.parse_args()
        username = request.json['UserName']
        password = request.json['Password']
        print("\n\n\nhere\n\n\n")

        user=Students.query.filter_by(Email=username).first()
        role="Student"
        print("\n\n\1\n\n\n")
        if user and  check_password_hash(user.Password , password):
            print("\n\n\2\n\n\n")
            
            expires = timedelta(days=30)
            additional_claims = {"role": role}
            token = create_access_token(
                identity=user.StudentID, 
                expires_delta=expires,
                additional_claims=additional_claims)
            return {'id':user.StudentID,
                    'name':user.FirstName + " " + user.LastName,
                    'role':role,
                    'token': token}
        user=Instructors.query.filter_by(Email=username).first()
        role="Instrucotr"
        print("\n\n\3\n\n\n")

        if user and  check_password_hash(user.Password , password):
            expires = timedelta(days=30)
            additional_claims = {"role": role}
            token = create_access_token(
                identity=user.InstructorID, 
                expires_delta=expires,
                additional_claims=additional_claims)
            return {'id':user.InstructorID,
                    'name':user.FirstName + " " + user.LastName,
                    'role':role,
                    'token': token}
        
        return "Incorrect Username or password" ,401


#############################################
'''
STUDENT
'''
#############################################

@StudentNamespace.route('/createstudent')
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

@StudentNamespace.route('/<int:stuID>')
class studentResource(Resource):
    def get(self,stuID):
        '''
        Get Student Info
        '''
        student = Students.query.filter_by(StudentID=stuID).first()

        if student:
            return student_schema.dump(student)
        return "Student not found",404
    @api.expect(student)
    def patch(self,studentId):
        '''
        Edit Student Info
        '''
        student = Students.query.filter_by(StudentID=studentId).first()

        #updating required fields
        for key in request.json.keys():
            if key == 'FirstName':
                student.FirstName = request.json[key]
            elif key == 'LastName':
                student.LastName = request.json[key]
            elif key == 'Email':
                student.Email = request.json[key]
        db.session.commit()

        return student_schema.dump(student), 200


@StudentNamespace.route('/studentByEmail/<string:email>')
class StudentByEmail(Resource):
    def get(self,email):
        '''
        Get Student Info
        '''
        student = Students.query.filter_by(Email=email).first()

        if student:
            return student_schema.dump(student)
        return abort(404, "Student not found")

#############################################
'''
INSTRUCTOR
'''
#############################################


@InstructorsNamespace.route('/createinstructor')
class instructorsResource(Resource):
    @api.expect(instructor)
    def post(self):

        new_instructor = Instructors()
        new_instructor.FirstName = request.json['FirstName']
        new_instructor.LastName = request.json['LastName']
        new_instructor.Email = request.json['Email']
        new_instructor.Password = generate_password_hash(request.json['Password'], method='sha256')

        instructor = Instructors.query.filter_by(Email=new_instructor.Email).first()
        if instructor:
            return "Email already taken", 400

        db.session.add(new_instructor)
        db.session.commit()
        return instructor_schema.dump(new_instructor), 201


@InstructorsNamespace.route('/<int:instructorID>')
class instructorResource(Resource):
    def get(self,instructorID):
        instructor = Instructors.query.filter_by(InstructorID=instructorID).first()

        if instructor:
            return student_schema.dump(instructor)
        return "Instructor not found",404
    
    def patch(self,instructorID):
        return

#############################################
'''
RESOURCE
'''
#############################################
@ResourceNamespace.route('/<int:courseID>/resources')
class resourcesResource(Resource):
    def post(self,courseID):
        # saving the file to the server
        fileType = request.headers['Content-Type'].split("/")[1]
        contentType = request.headers['Content-Type']
        fileName = request.headers['File-Name'] #TODO

        randomfileName = str(uuid.uuid4())
        with open(os.path.join(upload_folder, randomfileName+"."+fileType), "wb") as fp:
            fp.write(request.data)

        # saving the file's metadata to database
        new_resource = Resources()
        new_resource.FilePath = upload_folder
        new_resource.FileName = fileName +"."+ fileType
        new_resource.RandomFileName = randomfileName +"."+ fileType
        new_resource.ContentType = contentType
        new_resource.CourseID = int(courseID)
        new_resource.CreationDate = datetime.now()

        db.session.add(new_resource)
        db.session.commit()
        
        return {'resourceID':new_resource.ResourceID}, 201

@ResourceNamespace.route('/<int:courseID>/resources/<int:resourceID>')
class resourceResource(Resource):
    def get(self,courseID,resourceID):
        file = Resources.query.filter_by(ResourceID=int(resourceID)).first()
        if file:
            return resource_schema.dump(file), 200
        return '', 404
    
    def delete(self,courseID,resourceID):
        file = Resources.query.filter_by(ResourceID=int(resourceID)).first()
        if file:
            db.session.delete(file)
            db.session.commit()
            return '',200
        return {"message": "File not found"}, 404

@ResourceNamespace.route('/<int:courseID>/resources/<int:resourceID>/download')
class resourcesResourceOne(Resource):
    def get(self,courseID,resourceID):
        file = Resources.query.filter_by(ResourceID=int(resourceID)).first()
        if file:
            try:
                filePath = file.FilePath
                randomFileName = file.RandomFileName
                fileContent = None

                with open(os.path.join(filePath, randomFileName), "rb") as fp:
                    fileContent = fp.read()
                response = make_response(fileContent)
                response.headers.set('Content-Type', file.ContentType)
                return response
            except:
                return '', 404
        
        return '', 404

#############################################
'''
COURSE
'''
#############################################
@CourseNamespace.route('')
class coursesResource(Resource):
    @api.expect(course)
    def post(self):
       new_course = Courses()
       new_course.InstructorID = request.json['InstructorID']
       new_course.CourseTitle = request.json['CourseTitle']
       new_course.CourseDescription = request.json['CourseDescription']

       db.session.add(new_course)

    
       db.session.commit()
       print(new_course)
       return course_schema.dump(new_course),201
       


@CourseNamespace.route('<int:courseID>/student/<int:studentID>')
class deleteStudent(Resource):
    def delete(self,courseID,studentID):
        c = CourseStudents.query.filter_by(StudentID=studentID, CourseID=courseID).first()
        if not c:
            return 'Student Not Registered in this course', 400

        db.session.delete()
        db.session.commit()
        return "Successfully deleted ",200


@CourseNamespace.route('/<int:courseID>')
class courseResource(Resource):
    def get(self,courseID):
        result = Courses.query.filter_by(CourseID=courseID).first()

        if not result:
            return "Course Not Found", 404

        return course_schema.dump(result)
    
    @api.expect(courseStudents)
    def post(self,courseID):
        
        student = CourseStudents.query.filter_by(StudentID = request.json['StudentID'], CourseID= courseID).first()
        if student:
            abort(400, message="Student Already Registered")
        
        add_student = CourseStudents()
        add_student.CourseID = request.json['CourseID']
        add_student.StudentID = request.json['StudentID']

        db.session.add(add_student)
        db.session.commit()
        print("COMMIT")
        stu=ADDSTUDENT()
        stu.CourseID=add_student.CourseID
        print(Students.query.filter_by(StudentID=add_student.StudentID).first())
        stu.email = Students.query.filter_by(StudentID=add_student.StudentID).first().Email
        stu.name = Students.query.filter_by(StudentID=add_student.StudentID).first().FirstName +" "+ Students.query.filter_by(StudentID=add_student.StudentID).first().LastName
        return add_student_schema.dump(stu), 200
    
@CourseNamespace.route('/student/<int:courseID>')
class courseResourceOne(Resource):
    def get(self,courseID):
        studentID = 1
        course = Courses.query.filter_by(CourseID= courseID).first()
        if not course:
            return "Course Not Found", 404


        c = CourseStudents.query.filter_by(StudentID=studentID, CourseID=courseID).first()
        if not c:
            return 'You are not registered to this course', 400
            
        return course_schema.dump(course)

    
    # LIST OF STUDENTS IN A COURSE
@CourseNamespace.route('/<int:courseID>/students')
class courseResourceTwo(Resource):
    def get(self,courseID):
        courses = CourseStudents.query.filter_by(CourseID = courseID).all()
        students=[]
        for course in courses:
            student = StudentListSchema()
            s = Students.query.filter_by(StudentID = course.StudentID).first()
            student.name= s.FirstName + " " + s.LastName
            student.email = s.Email
            student.id = s.StudentID
            students.append(student)


        # TODO : Create Schema
        return studentList_schema.dump(students)

    # def post(self,courseID):

    #     return 
# A STUDENTS LIST OF COURSES
@CourseNamespace.route('/studentcourses')
class courseResourceThree(Resource):
    def get(self):
        # TODO fetch real student Id
        student_id = 1
        courses= CourseStudents.query.filter_by(StudentID=student_id).all()
        lst =[]

        for course in courses:
            a= COURSES()
            c = Courses.query.filter_by(CourseID = course.CourseID).first()
            a.CourseId = course.CourseID
            a.CourseTitle = c.CourseTitle
            a.CourseDescription = c.CourseDescription
            a.InstructorID = c.InstructorID
            lst.append(a)

        return courses_schema.dump(lst)

@CourseNamespace.route('/studentcourses/<int:courseID>')
class courseResourceFour(Resource):
    def get(self,courseID):
        student_id = get_jwt_identity()
        course= CourseStudents.query.filter_by(StudentID=student_id, CourseID=courseID).first()
        if course:
            return Courses.query.filter_by(courseID = courseID).first()
        return abort(404, 'Student Not enrolled')

@CourseNamespace.route('/instructorcourses')
class courseResourceFive(Resource):
    def get(self):
        instructor_id = 1
        courses= Courses.query.filter_by(InstructorID=instructor_id).all()
        lst =[]

        for course in courses:
            a= COURSES()
            c = Courses.query.filter_by(CourseID = course.CourseID).first()
            a.CourseId = course.CourseID
            a.CourseTitle = c.CourseTitle
            a.CourseDescription = c.CourseDescription
            a.InstructorID = c.InstructorID
            lst.append(a)
        return courses_schema.dump(lst)

    

#############################################
'''
CLASSROOM
'''
#############################################

@ClassroomNamspace.route('/<int:courseID>/classrooms/<int:classroomID>')
class classroomResource(Resource):
    def get(self,courseID,classroomID):
        classroom = VirtualClassrooms.query.filter_by(ClassroomID=classroomID, CourseID=courseID).first()
        if not classroom:
            return "Classroom Not Found", 404
        return classroom_schema.dump(classroom), 200
    
    def delete(self,courseID,classroomID):
        classroom = VirtualClassrooms.query.filter_by(ClassroomID=classroomID, CourseID=courseID).first()
        if not classroom:
            return "Classroom not found", 404
        db.session.delete(classroom)
        db.session.commit()
        return "Successfully deleted",204

@ClassroomNamspace.route('/<int:courseID>/classrooms/<int:classroomID>/attendance')
class classroomResource(Resource):
    def get(self,courseID,classroomID):
        classroom = VirtualClassrooms.query.filter_by(ClassroomID=classroomID, CourseID=courseID).first()
        if not classroom:
            return "Classroom Not Found", 404
        class_stu = ClassroomStudents.query.filter_by(ClassroomID=classroomID).all()
        students=[]
        for stu in class_stu:
            student = StudentListSchema()
            s = Students.query.filter_by(StudentID = stu.StudentID).first()
            student.name= s.FirstName + " " + s.LastName
            student.email = s.Email
            student.id = s.StudentID
            students.append(student)


        return studentList_schema.dump(students)
    

@ClassroomNamspace.route('/<int:courseID>/classrooms')
class classroomResourceOne(Resource):
    def get(self,courseID):
        classrooms = VirtualClassrooms.query.all()
        if not classrooms:
            return "No classrooms available"
        return classrooms_schema.dump(classrooms), 200
    
    @api.expect(classroom)
    def post(self,courseID):
        new_classroom = VirtualClassrooms()
        new_classroom.ClassroomName = request.json['ClassroomName']
        new_classroom.CourseID = courseID
        new_classroom.Date = datetime.strptime(request.json['Date'],"%d/%m/%y").strftime('%d/%m/%y')
        new_classroom.StartTime = request.json['StartTime']
        new_classroom.EndTime = request.json['EndTime']
        course =Courses.query.get(courseID)
        if course == None:
            return "Course does not exist",404

        db.session.add(new_classroom)
        db.session.commit()
        return classroom_schema.dump(new_classroom),201
    

@ClassroomNamspace.route('/<int:courseID>/classrooms/<int:classroomID>/join')
class classroomResourceTwo(Resource):
    def get(self,courseID,classroomID):
        return 

if __name__ == "__main__":
    app.run(debug=True)