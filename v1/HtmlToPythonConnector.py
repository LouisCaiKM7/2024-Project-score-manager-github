from flask import Flask, request, jsonify, render_template, redirect, session
import os
import sqlite3
import ScoreAnalyzer
import UsersDatabaseProcessor
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
        UsersDatabaseProcessor.cur.execute("SELECT * FROM Users WHERE email = ?", (email,))
        user = UsersDatabaseProcessor.cur.fetchone()
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            return redirect('/upload')
        return "Invalid email or password", 401
    return render_template('login.html')

# Signup Route
@App.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        try:
            UsersDatabaseProcessor.cur.execute("INSERT INTO Users (email, password) VALUES (?, ?)", (email, hashed_password))
            UsersDatabaseProcessor.conn.commit()
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

# Logout Route
@App.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

if __name__ == '__main__':
    App.run(debug=True)

login()


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
