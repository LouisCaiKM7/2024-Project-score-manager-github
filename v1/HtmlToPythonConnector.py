from flask import Flask, request, jsonify, render_template
import os
import ScoreAnalyzer

App = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@App.route('/')
def index():
    return render_template('Index.html')

@App.route('/upload', methods=['POST'])
def upload_file():
    if 'studentsFile' not in request.files or 'scoresFile' not in request.files:
        return jsonify({'error': 'Please upload both files'}), 400

    StudentFile = request.files['studentsFile']
    ScoresFile = request.files['scoresFile']

    if StudentFile.filename == '' or ScoresFile.filename == '':
        return jsonify({'error': 'No selected files'}), 400

    StudentFilePath = os.path.join(UPLOAD_FOLDER, StudentFile.filename)
    ScoresFilePath = os.path.join(UPLOAD_FOLDER, ScoresFile.filename)
    StudentFile.save(StudentFilePath)
    ScoresFile.save(ScoresFilePath)

    ScoreAnalyzer.main(StudentFilePath, ScoresFilePath)

    return jsonify({'message': 'Files uploaded and processed successfully'})

if __name__ == '__main__':
    App.run(debug=True)
