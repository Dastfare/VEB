from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this to a secure secret key
db = SQLAlchemy(app)

# Define the Welder model
class Welder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    department_number = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Plain text password

    def __init__(self, surname, name, birthdate, department_number, experience, city, region, gender, password):
        self.surname = surname
        self.name = name
        self.birthdate = birthdate
        self.department_number = department_number
        self.experience = experience
        self.city = city
        self.region = region
        self.gender = gender
        self.password = password  # Store plain text password

    def check_password(self, password):
        return self.password == password  # Compare plain text passwords directly

# Define the AdminProfile model
class AdminProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

first_request = True

@app.before_request
def create_tables():
    global first_request

    if first_request:
        db.create_all()

        admin_profile = AdminProfile.query.first()

        if not admin_profile:
            admin = AdminProfile(login='admin', password='admin')
            db.session.add(admin)
            db.session.commit()

            first_request = False

# Main page
@app.route('/')
def index():
    return render_template('index.html')

# Welder login page
@app.route('/welder_login', methods=['GET', 'POST'])
def welder_login():
    if request.method == 'POST':
        surname = request.form['surname']
        name = request.form['name']
        password = request.form['password']

        welder = Welder.query.filter_by(surname=surname, name=name).first()
        if welder and welder.check_password(password):  # Check password directly
            session['welder_id'] = welder.id
            return redirect(url_for('welder_profile'))
        else:
            return "Неправильный логин или пароль. Повторите попытку!"
    return render_template('welder_login.html')

# Admin login page
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin_profile = AdminProfile.query.filter_by(login=username, password=password).first()
        if admin_profile:
            return redirect(url_for('admin_profile'))
        else:
            return "Неправильный логин или пароль. Повторите попытку!"
    return render_template('admin_login.html')

# Admin profile page
@app.route('/admin_profile')
def admin_profile():
    return render_template('admin_profile.html')

# Admin redirection logic
@app.route('/admin_redirect', methods=['POST'])
def admin_redirect():
    if request.method == 'POST':
        action = request.form['action']
        if action == 'welders':
            return redirect(url_for('welders'))
        elif action == 'register_welder':
            return redirect(url_for('register_welder'))
        else:
            return redirect(url_for('admin_profile'))

# Welder registration page
@app.route('/register_welder', methods=['GET', 'POST'])
def register_welder():
    if request.method == 'POST':
        surname = request.form['surname']
        name = request.form['name']
        birthdate_str = request.form['birthdate']  # Get birthdate as string
        birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()  # Convert string to date object
        department_number = request.form['department_number']
        experience = int(request.form['experience'])  # Convert experience to integer
        city = request.form['city']
        region = request.form['region']
        gender = request.form['gender']
        password = request.form['password']  # Retrieve password from form

        # Create a new Welder object with the provided information
        new_welder = Welder(surname=surname, name=name, birthdate=birthdate, department_number=department_number,
                            experience=experience, city=city, region=region, gender=gender, password=password)

        # Add the new welder to the database session and commit changes
        db.session.add(new_welder)
        db.session.commit()

        # Redirect to the welder's profile after successful registration
        return redirect(url_for('welder_profile'))

    return render_template('register_welder.html')

# Welder profile page
@app.route('/welder_profile')
def welder_profile():
    # Check if welder is logged in
    if 'welder_id' in session:
        # Retrieve welder's data from the database based on their ID
        welder = Welder.query.get(session['welder_id'])
        # Render the profile template with the welder's data
        return render_template('welder_profile.html', welder=welder)
    else:
        # If welder is not logged in, redirect to the login page
        return redirect(url_for('welder_login'))

# List of welders page
@app.route('/welders')
def welders():
    welders_list = Welder.query.all()
    return render_template('welders.html', welders=welders_list)

if __name__ == '__main__':
    app.run(debug=True)