from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from config import Config

app = Flask(__name__)
CORS(app, origins=Config.CORS_ORIGINS)

# MongoDB connection
client = MongoClient(Config.MONGO_URI)
db = client[Config.DATABASE_NAME]

# Collections
students = db['students']
faculties = db['faculties']
courses = db['courses']
leaves = db['leaves']
timetable = db['timetable']

# Helper function to convert ObjectId to string
def serialize_doc(doc):
    if doc is None:
        return None
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

# Students endpoints
@app.route('/api/students', methods=['GET'])
def get_students():
    try:
        students_list = list(students.find())
        for student in students_list:
            student['_id'] = str(student['_id'])
        return jsonify(students_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<student_id>', methods=['GET'])
def get_student(student_id):
    try:
        student = students.find_one({'_id': ObjectId(student_id)})
        return jsonify(serialize_doc(student))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Faculties endpoints
@app.route('/api/faculties', methods=['GET'])
def get_faculties():
    try:
        faculties_list = list(faculties.find())
        for faculty in faculties_list:
            faculty['_id'] = str(faculty['_id'])
            # Convert subject ObjectIds to strings
            if 'subjects' in faculty:
                faculty['subjects'] = [str(subject_id) for subject_id in faculty['subjects']]
        return jsonify(faculties_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/faculties/<faculty_id>', methods=['GET'])
def get_faculty(faculty_id):
    try:
        faculty = faculties.find_one({'_id': ObjectId(faculty_id)})
        if faculty and 'subjects' in faculty:
            faculty['subjects'] = [str(subject_id) for subject_id in faculty['subjects']]
        return jsonify(serialize_doc(faculty))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Courses endpoints
@app.route('/api/courses', methods=['GET'])
def get_courses():
    try:
        courses_list = list(courses.find())
        for course in courses_list:
            course['_id'] = str(course['_id'])
            if 'facultyInCharge' in course:
                course['facultyInCharge'] = str(course['facultyInCharge'])
        return jsonify(courses_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/courses/<course_id>', methods=['GET'])
def get_course(course_id):
    try:
        course = courses.find_one({'_id': ObjectId(course_id)})
        if course and 'facultyInCharge' in course:
            course['facultyInCharge'] = str(course['facultyInCharge'])
        return jsonify(serialize_doc(course))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Leaves endpoints
@app.route('/api/leaves', methods=['GET'])
def get_leaves():
    try:
        leaves_list = list(leaves.find())
        for leave in leaves_list:
            leave['_id'] = str(leave['_id'])
            if 'studentId' in leave:
                leave['studentId'] = str(leave['studentId'])
            if 'handledBy' in leave:
                leave['handledBy'] = str(leave['handledBy'])
        return jsonify(leaves_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/leaves/<leave_id>', methods=['GET'])
def get_leave(leave_id):
    try:
        leave = leaves.find_one({'_id': ObjectId(leave_id)})
        if leave:
            if 'studentId' in leave:
                leave['studentId'] = str(leave['studentId'])
            if 'handledBy' in leave:
                leave['handledBy'] = str(leave['handledBy'])
        return jsonify(serialize_doc(leave))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Timetable endpoints
@app.route('/api/timetable', methods=['GET'])
def get_timetable():
    try:
        timetable_data = list(timetable.find())
        for day in timetable_data:
            day['_id'] = str(day['_id'])
        return jsonify(timetable_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/timetable/<day_name>', methods=['GET'])
def get_timetable_day(day_name):
    try:
        day_data = timetable.find_one({'dayOfWeek': day_name})
        return jsonify(serialize_doc(day_data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Dashboard stats endpoint
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_stats():
    try:
        stats = {
            'totalStudents': students.count_documents({}),
            'totalFaculties': faculties.count_documents({}),
            'totalCourses': courses.count_documents({}),
            'totalLeaves': leaves.count_documents({}),
            'totalTimetableDays': timetable.count_documents({})
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=Config.FLASK_DEBUG, port=Config.FLASK_PORT, host='0.0.0.0')
