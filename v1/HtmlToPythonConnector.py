
from flask import Flask, request, jsonify, render_template, redirect, session
import os
import sqlite3
import ScoreAnalyzer
import UsersDatabaseProcessor
import ScoresDataBaseProcessor
import Constant
from werkzeug.security import generate_password_hash, check_password_hash

App = Flask(__name__)
App.secret_key = 'your_secret_key'  # Needed to use sessions

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Database setup for users


# Home Route
@App.route('/')
def home():
    if 'user_id' in session:
        return redirect('/upload')
    return redirect('/login')

# Login Route
@App.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # password = request.form['password']
        # id = request.form['id']
        UsersDatabaseProcessor.Cur.execute("SELECT * FROM Users WHERE email = ?", (email,))
        user = UsersDatabaseProcessor.Cur.fetchone()
        print(user,check_password_hash(user[2], password))
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            return redirect('/upload')
        return "Invalid email or password", 401
    return render_template('login.html')



@App.route('/login_students', methods=['GET', 'POST'])
def login_students():
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        UsersDatabaseProcessor.Cur.execute("SELECT * FROM Students WHERE id = ?", (id,))
        user = UsersDatabaseProcessor.Cur.fetchone()
        print(user,check_password_hash(user[1], password))
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            return redirect('/students_page')
        return "Invalid email or password", 401
    return render_template('studentslogin.html')

@App.route('/students_page', methods=['GET', 'POST'])
def studentpage():
    user_id = '0000'+ str(session.get('user_id'))
    print(user_id)
    ScoresDataBaseProcessor.Cursor.execute("SELECT Score FROM Scores WHERE id = ?", (user_id,))
    score = ScoresDataBaseProcessor.Cursor.fetchall()
    print(score)
    return render_template('studentspage.html',score = score)
# Signup Route
@App.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        try:
            UsersDatabaseProcessor.Cur.execute("INSERT INTO Users (email, password) VALUES (?, ?)", (email, hashed_password))
            UsersDatabaseProcessor.Conn.commit()
            return redirect('/login')
        except sqlite3.IntegrityError:
            return "Email already exists", 400
    return render_template('signup.html')

# Upload Route (only accessible if logged in)
@App.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        if 'studentsFile' not in request.files or 'scoresFile' not in request.files:
            return render_template('index.html', error='Please upload both files')

        StudentFile = request.files['studentsFile']
        ScoresFile = request.files['scoresFile']

        if StudentFile.filename == '' or ScoresFile.filename == '':
            return render_template('index.html', error='No selected files')

        StudentFilePath = os.path.join(UPLOAD_FOLDER, StudentFile.filename)
        ScoresFilePath = os.path.join(UPLOAD_FOLDER, ScoresFile.filename)
        StudentFile.save(StudentFilePath)
        ScoresFile.save(ScoresFilePath)

        try:
            ScoreAnalyzer.main(StudentFilePath, ScoresFilePath)
            success_message = f"File '{ScoresFile.filename}' and '{StudentFile.filename}' uploaded and processed successfully"
            return render_template('index.html', message=success_message)
        except Exception as e:
            return render_template('index.html', error=str(e))

    return render_template('index.html')

@App.route('/submit_student', methods=['POST'])
def submit_student():
    student_name = request.form['studentName']
    student_id = request.form['studentID']
    
    try:
        # Insert the student into the database
        ScoresDataBaseProcessor.Cursor.execute("INSERT OR IGNORE INTO Students (id, Name) VALUES (?, ?)", (student_name,student_id ))
        ScoresDataBaseProcessor.Conn.commit()

        # Return a message or redirect to another page
        return f"Student {student_name} with ID {student_id} added successfully!"
    except Exception as e:
        return f"Error: {str(e)}"
# Route to handle score form submission
@App.route('/submit_score', methods=['POST'])
def submit_score():
    student_id = request.form['studentID']
    score = request.form['score']
    
    try:
        ScoreAnalyzer.open_database()
        # Insert the score into the database
        ScoresDataBaseProcessor.Cursor.execute("INSERT OR IGNORE INTO Scores (id, Score) VALUES (?, ?)", (student_id, int(score)))
        ScoresDataBaseProcessor.Conn.commit()
        ScoreAnalyzer.DirectlyInsert()
        return f"Score {score} added for student ID {student_id}!"
    except Exception as e:
        return f"Error: {str(e)}"

# Logout Route
@App.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

if __name__ == '__main__':
    App.run(debug=True)




# from flask import Flask, request, jsonify, render_template
# import os
# import ScoreAnalyzer

# App = Flask(__name__)

# UPLOAD_FOLDER = 'uploads'
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# @App.route('/')
# def index():
#     return render_template('Index.html')

# @App.route('/upload', methods=['POST'])
# def upload_file():
#     if 'studentsFile' not in request.files or 'scoresFile' not in request.files:
#         return jsonify({'error': 'Please upload both files'}), 400

#     StudentFile = request.files['studentsFile']
#     ScoresFile = request.files['scoresFile']

#     if StudentFile.filename == '' or ScoresFile.filename == '':
#         return jsonify({'error': 'No selected files'}), 400

#     StudentFilePath = os.path.join(UPLOAD_FOLDER, StudentFile.filename)
#     ScoresFilePath = os.path.join(UPLOAD_FOLDER, ScoresFile.filename)
#     StudentFile.save(StudentFilePath)
#     ScoresFile.save(ScoresFilePath)

    
#     print(StudentFilePath,ScoresFilePath)
#     try:
#         # Call the Python function to handle the CSV and database processing
#         ScoreAnalyzer.main(StudentFilePath, ScoresFilePath)
#         return jsonify({'message': f"File '{ScoresFile}' and '{StudentFile}' uploaded and processed successfully"}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     App.run(debug=True)


# upload_file()
