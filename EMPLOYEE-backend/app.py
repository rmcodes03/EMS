from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
from flask_mail import Mail, Message
import random


app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app, resources={
    r"/auth/*": {"origins": "http://localhost:5173"},
    r"/leave/add": {"origins": "http://localhost:5173"},
    r"/api/*": {"origins": "http://localhost:5173"}
}, supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databse.db'
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'rushideshmukh824@gmail.com'
app.config['MAIL_PASSWORD'] = 'tedyohlefvpoknmx'
mail = Mail(app)

class AdminData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    def __init__(self, email, password):
        self.email = email
        self.password = password

class EmpData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    empid = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Integer)
    category = db.Column(db.String(100), nullable=False)
    def __init__(self, name, email, empid, password, salary, category):
        self.name = name
        self.email = email
        self.empid = empid
        self.password = password
        self.salary = salary
        self.category = category

class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    empid = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    numberOfDays = db.Column(db.Integer, nullable=False)
    fromDate = db.Column(db.DateTime, nullable=False)
    toDate = db.Column(db.DateTime, nullable=False)
    def __init__(self, name, empid, reason, numberOfDays, fromDate, toDate):
        self.name = name
        self.empid = empid
        self.reason = reason
        self.numberOfDays = numberOfDays
        self.fromDate = fromDate
        self.toDate = toDate

class ProjectList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    def __init__(self, name):
        self.name = name

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    projectName = db.Column(db.String(100), nullable=False)
    tag = db.Column(db.String(100))
    timeElapsed = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'projectName': self.projectName,
            'tag': self.tag,
            'timeElapsed': self.timeElapsed
        }

class TagList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(100), nullable=False)

    def __init__(self, tag):
        self.tag = tag

with app.app_context():
    db.create_all()

admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')
admin.add_view(ModelView(AdminData, db.session))
admin.add_view(ModelView(EmpData, db.session))
admin.add_view(ModelView(Leave, db.session))
admin.add_view(ModelView(ProjectList, db.session))
admin.add_view(ModelView(Project, db.session))
admin.add_view(ModelView(TagList, db.session))

@app.route('/auth/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    adminData = AdminData.query.filter_by(email=email).first()
    if  adminData and adminData.password == password:
        print('Login successful')
        session['logged_in'] = True
        return jsonify({'loginStatus': True}), 200
    else:
        return jsonify({'loginStatus': False, 'Error': 'Invalid credentials'}), 401

@app.route('/auth/add_employee', methods=['GET', 'POST'])
def addEmp():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    empid = data.get('employee_id')
    password = data.get('password')
    salary = data.get('salary')
    category = data.get('category_id')

    new_emp = EmpData(name=name, email=email, empid=empid, password=password, salary=salary, category=category)
    db.session.add(new_emp)
    db.session.commit()

    return jsonify({'message': 'Employee added successfully'}), 200

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    data = request.json
    empid = data.get('empid')
    password = data.get('password')
    user = EmpData.query.filter_by(empid=empid).first()
    if  user and user.password == password:
        print('Login successful')
        session['logged_in'] = True
        session['empid'] = empid
        return jsonify({'loginStatus': True}), 200
    else:
        return jsonify({'loginStatus': False, 'Error': 'Invalid credentials'}), 401

@app.route('/auth/employee', methods=['GET', 'POST'])
def get_employee_data():
    if 'logged_in' not in session or not session['logged_in']:
        return jsonify({'error': 'Not logged in'}), 401

    # Get the logged-in employee's data from the database
    empid = session['empid']
    user = EmpData.query.filter_by(empid=empid).first()
    if not user:
        return jsonify({'error': 'Employee not found'}), 404

    return jsonify({
        'name': user.name,
        'email': user.email,
        'password': user.password
    }), 200

@app.route('/auth/employees', methods=['GET', 'POST'])
def get_employees():
    employees = EmpData.query.all()
    employee_list = []
    for employee in employees:
        employee_dict = {
            'name': employee.name,
            'email': employee.email,
            'employee_id': employee.empid,
            'salary': employee.salary,
            'category': employee.category
        }
        employee_list.append(employee_dict)
    return jsonify({'Status': True, 'Result': employee_list}), 200

@app.route('/leave/add', methods=['GET', 'POST'])
def add_leave():
    data = request.json
    name = data.get('name')
    empid = data.get('employeeId')
    reason = data.get('reason')
    numberOfDays = data.get('numberOfDays')

    fromDate = datetime.strptime(data.get('fromDate'), '%Y-%m-%d')
    toDate = datetime.strptime(data.get('toDate'), '%Y-%m-%d')

    # Create a new Leave instance and add it to the database
    new_leave = Leave(name=name, empid=empid, reason=reason, numberOfDays=numberOfDays, fromDate=fromDate, toDate=toDate)
    db.session.add(new_leave)
    db.session.commit()

    return jsonify({'message': 'Leave added successfully'}), 200


@app.route('/api/add_projects', methods=['GET', 'POST'])
def add_project():
    data = request.json
    project_name = data.get('name')

    # Check if the project already exists
    existing_project = ProjectList.query.filter_by(name=project_name).first()
    if existing_project:
        return jsonify({'error': 'Project already exists'}), 400

    # If the project doesn't exist, add it to the database
    new_project = ProjectList(name=project_name)
    db.session.add(new_project)
    db.session.commit()

    return jsonify({'message': 'Project added successfully'}), 201


@app.route('/api/projects', methods=['GET', 'POST'])  # Allow both GET and POST requests
def handle_projects():
    if request.method == 'GET':
        projects = Project.query.all()
        projects_data = [project.to_dict() for project in projects]
        return jsonify(projects_data), 200
    elif request.method == 'POST':
        data = request.json
        if not data.get('projectName').strip():
            return jsonify({'error': 'Project name is required!'}), 400

        new_project = Project(projectName=data.get('projectName'), tag=data.get('tag'), timeElapsed=data.get('timeElapsed'))
        db.session.add(new_project)
        db.session.commit()

        return jsonify({'message': 'Project added successfully!'}), 201

@app.route('/api/project_list', methods=['GET'])
def get_project_list():
    # Query the database to fetch all project names
    projects = ProjectList.query.all()
    # Extract project names and return as JSON response
    project_names = [project.name for project in projects]
    return jsonify(project_names)

@app.route('/api/tag_list', methods=['GET'])
def get_tag_list():
    tags = TagList.query.all()
    tags_list = [{'id': tag.id, 'tag': tag.tag} for tag in tags]
    return jsonify({'tags': tags_list})

@app.route('/api/add_tag', methods=['POST'])
def add_tag():
    data = request.json
    tag_name = data.get('tag')

    # Check if the tag already exists
    existing_tag = TagList.query.filter_by(tag=tag_name).first()
    if existing_tag:
        return jsonify({'error': 'Tag already exists'}), 400

    # If the tag doesn't exist, add it to the database
    new_tag = TagList(tag=tag_name)
    db.session.add(new_tag)
    db.session.commit()

    return jsonify({'message': 'Tag added successfully'}), 201


@app.route('/auth/forgotpassword', methods=['GET', 'POST'])
def forgot_password():
    data = request.json
    email = data.get('email')
    user = EmpData.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    otp = random.randint(100000, 999999)  # Generate OTP
    session['otp'] = otp
    session['email'] = email

    # Here you would normally send the OTP to the user's email or phone number
    # Send OTP via email
    msg = Message('Password Reset OTP', sender='rushi', recipients=[email])
    msg.body = f'Your OTP for password reset is: {otp}'
    mail.send(msg)

    # For simplicity, we'll just return the OTP in the response
    return jsonify({'message': 'OTP sent successfully', 'otp': otp}), 200


@app.route('/auth/resetpassword', methods=['GET', 'POST'])
def reset_password():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('password')

    session['otp'] = otp
    session['email'] = email
    # Verify the OTP
    session_otp = session.get('otp')
    session_email = session.get('email')

    if (not session_email) or (not session_otp) or (session_email != email) or (int(session_otp) != int(otp)):
        return jsonify({'error': 'Invalid or expired OTP'}), 401

    # Find the user by email
    user = EmpData.query.filter_by(email=email).first()
    if not user:
        print('User not found')
        return jsonify({'error': 'User not found'}), 404

    # Update the user's password
    user.password = new_password
    db.session.commit()
    return jsonify({'message': 'Password reset successful'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
