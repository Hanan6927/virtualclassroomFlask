import datetime
from flask_restplus.fields import ClassName
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from marshmallow.fields import Email


db=SQLAlchemy()
class Students(db.Model):
    __tablename__ = "students"
    StudentID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String, nullable=False)
    LastName = db.Column(db.String, nullable=True)
    Email = db.Column(db.String, nullable=False)
    Password = db.Column(db.String, nullable=False)

class Instructors(db.Model):
    __tablename__ = "instructors"
    InstructorID = db.Column(db.Integer, primary_key=True)
    Password = db.Column(db.String, nullable=False)
    FirstName = db.Column(db.String, nullable=False)
    LastName = db.Column(db.String, nullable=True)
    Email = db.Column(db.String, nullable=False)
    # Courses = db.relationship('Course', backref='instructor', lazy=True)


class Courses(db.Model):
    __tablename__ = "courses"
    CourseID = db.Column(db.Integer, primary_key=True)
    InstructorID = db.Column(db.Integer, db.ForeignKey(
        "instructors.InstructorID"), nullable=False)
    CourseTitle = db.Column(db.String, nullable=False)
    CourseDescription = db.Column(db.String, nullable=True)
    ClassRooms = db.relationship('VirtualClassrooms', backref='Course', lazy=True)


class CourseStudents(db.Model):
    __tablename__ = "coursestudents"
    CourseID = db.Column(db.Integer, db.ForeignKey(
        "courses.CourseID"), nullable=False, primary_key=True)
    StudentID = db.Column(db.Integer, db.ForeignKey(
        "students.StudentID"), nullable=False, primary_key=True)

class Resources(db.Model):
    __tablename__ = "resources"
    ResourceID = db.Column(db.Integer, primary_key=True)
    FilePath = db.Column(db.String, nullable=False)
    FileName = db.Column(db.String, nullable=False)
    RandomFileName = db.Column(db.String, nullable=False)
    ContentType = db.Column(db.String, nullable=False)
    CourseID = db.Column(db.Integer, db.ForeignKey(
        "courses.CourseID"), nullable=False)
    CreationDate = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    Course = db.relationship('Courses', backref='resources', lazy=True)


class VirtualClassrooms(db.Model):
    __tablename__ = "virtualclassrooms"
    ClassroomID = db.Column(db.Integer, primary_key=True)
    ClassroomName = db.Column(db.String, nullable=False)
    Date = db.Column(db.DateTime)
    CourseID = db.Column(db.Integer, db.ForeignKey(
        "courses.CourseID"), nullable=False)
    StartTime = db.Column(db.String, nullable=False)
    EndTime = db.Column(db.String, nullable=False)
    
    
 
class ClassroomStudents(db.Model):
    __tablename__ = "classroomstudents"
    ID = db.Column(db.Integer, primary_key=True)
    ClassroomID = db.Column(db.Integer, db.ForeignKey(
        "virtualclassrooms.ClassroomID"), nullable=False, primary_key=True)
    StudentID = db.Column(db.Integer, db.ForeignKey(
        "students.StudentID"), nullable=False , primary_key=True)