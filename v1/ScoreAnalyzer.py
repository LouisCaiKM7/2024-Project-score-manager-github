import csv
import os
import Constant
import ScoresDataBaseProcessor
import sqlite3
import UsersDatabaseProcessor
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify
import uuid


ScoresDataBaseProcessor.Excecuter()


def open_database():
    ScoresDataBaseProcessor.Conn = sqlite3.connect(Constant.DatabaseFile, check_same_thread=False)
    ScoresDataBaseProcessor.Cursor = ScoresDataBaseProcessor.Conn.cursor()

def close_database():
    if ScoresDataBaseProcessor.Conn:
        ScoresDataBaseProcessor.Conn.commit()  # Ensure all changes are committed
        ScoresDataBaseProcessor.Conn.close()


# def MergeStudentsAndScores():
#     ScoresDataBaseProcessor.Cursor.execute('''
#         SELECT Students.Name, Scores.Score 
#         FROM Students 
#         JOIN Scores ON Students.id = Scores.id
#     ''')
#     PeopleScores = ScoresDataBaseProcessor.Cursor.fetchall()

#     for name, score in PeopleScores:
#         GlobalScore[name] = score

#     return PeopleScores
def generate_unique_id():
    return str(uuid.uuid4())  

def InsertStudentsandScores(Student,Score):
    ScoresDataBaseProcessor.Cursor.execute("SELECT id FROM Students WHERE Name = ?", (Student,))
    result = ScoresDataBaseProcessor.Cursor.fetchone()

    if result:  # If student exists, use the existing ID
        StudentID = result[0]
        print(f"Student {Student} already exists with ID {StudentID}.")
    else:  # Generate new ID if the student doesn't exist
        StudentID = generate_unique_id()
        print(f"New ID generated for {Student}: {StudentID}")
        ScoresDataBaseProcessor.Cursor.execute(
            "INSERT INTO Students (id, Name) VALUES (?, ?)", (StudentID, Student)
        
        )
        ScoresDataBaseProcessor.Conn.commit()

    # Add to Students and ScoresDict
    ScoresDataBaseProcessor.Cursor.execute(
        "INSERT OR IGNORE INTO Scores (id, Score) VALUES (?, ?)", (StudentID, int(Score)))
    ScoresDataBaseProcessor.Cursor.execute(
        "INSERT OR IGNORE INTO Results (Name, Score) VALUES (?, ?)", (Student, int(Score)))
    ScoresDataBaseProcessor.Conn.commit()
    
def ReadStudent(FileName):
    Students = {}
    ScoresDict = {}
    
    with open(FileName, 'r') as File:
        CsvReader = csv.reader(File)
        next(CsvReader)  # Skip header row if present

        for Row in CsvReader:
            Name, Score = Row
            
            # Check if the student exists in the database
            ScoresDataBaseProcessor.Cursor.execute("SELECT id FROM Students WHERE Name = ?", (Name,))
            result = ScoresDataBaseProcessor.Cursor.fetchone()

            if result:  # If student exists, use the existing ID
                StudentID = result[0]
                print(f"Student {Name} already exists with ID {StudentID}.")
            else:  # Generate new ID if the student doesn't exist
                StudentID = generate_unique_id()
                print(f"New ID generated for {Name}: {StudentID}")
                ScoresDataBaseProcessor.Cursor.execute(
                    "INSERT INTO Students (id, Name) VALUES (?, ?)", (StudentID, Name)
                )

            # Add to Students and ScoresDict
            Students[StudentID] = Name
            ScoresDict[StudentID] = int(Score)
            ScoresDataBaseProcessor.Cursor.execute(
                "INSERT OR IGNORE INTO Scores (id, Score) VALUES (?, ?)", (StudentID, int(Score))
            )

        print(Students)
        return Students, ScoresDict


# def ReadScore(FileName):
#     Score = {}
#     with open(FileName, 'r') as File:
#         CsvReader = csv.reader(File)
#         next(CsvReader) 
#         for Row in CsvReader:
#             StudentID = generate_unique_id()
#             Name, Score = Row
             
#             Score[StudentID] = Score
#         print(Score)
#         return Score

# def ReadScores(FileName):
#     Scores = {}

#     with open(FileName, 'r') as File:
#         CsvReader = csv.reader(File)
#         next(CsvReader)  

#         for Row in CsvReader:
#             StudentID, Score = Row
#             Scores[StudentID] = int(Score) 
#         return Scores
def MergeStudentsAndScores(Students, ScoresDict):
    PeopleScores = []

    for StudentID, Name in Students.items():
        if StudentID in ScoresDict:
            PeopleScores.append((Name, ScoresDict[StudentID]))  # Match name with score
    print(PeopleScores)

    return PeopleScores


def InsertStudentsAndPasswords(): 
    # Fetch student IDs from the Scores database
    ScoresDataBaseProcessor.Cursor.execute("SELECT id FROM Students")
    Peopleid = ScoresDataBaseProcessor.Cursor.fetchall()
    
    # Print fetched data for debugging
    print(f"Fetched People IDs: {Peopleid}")
    
    for person in Peopleid:
        # 'person' is a tuple, so we need to get the first element (the ID)
        student_id = person[0]
        
        # Print the student ID being processed
        print(f"Processing Student ID: {student_id}")
        
        # Check if the id already exists in the Users database
        UsersDatabaseProcessor.Cur.execute("SELECT id FROM Students WHERE id = ?", (str(student_id),))
        existing_record = UsersDatabaseProcessor.Cur.fetchone()
        
        # If no existing record is found, insert the new student
        if not existing_record:
            print(f"Inserting new user for student ID {student_id}")
            UsersDatabaseProcessor.Cur.execute(
                "INSERT INTO Students (id, password) VALUES (?, ?)",
                (str(student_id), generate_password_hash(str(student_id)))
            )
        else:
            print(f"Skipping {student_id}, already exists.")

    # Commit the transaction
    UsersDatabaseProcessor.Conn.commit()
    
    print("Executed")




def CalculateAverageScores():
    ScoresDataBaseProcessor.Cursor.execute("SELECT Score FROM Results")
    Scores = ScoresDataBaseProcessor.Cursor.fetchall()


    if not Scores:
        return 0  
    TotalScores = [score[0] for score in Scores if isinstance(score[0], int)]  # Filter to avoid non-integer scores

    AverageScore = "{:.2f}".format(sum(TotalScores) / len(TotalScores)) if TotalScores else 0
    return AverageScore

def RankPeople(PeopleScores):
    RankedPeople = sorted(PeopleScores, key=lambda x: x[1], reverse=True)
    return RankedPeople


def WritingResultsToDatabase(RankedPeople):
    for Name, Score in RankedPeople:
        ScoresDataBaseProcessor.Cursor.execute("INSERT OR IGNORE INTO Results (Name, Score) VALUES (?, ?)", (Name, Score))
        print("a")
    ScoresDataBaseProcessor.Conn.commit()

    


def ExportResultsToCSV(CsvFile):
    
    ScoresDataBaseProcessor.Cursor.execute("SELECT Name, Score FROM Results")
 
    Rows = ScoresDataBaseProcessor.Cursor.fetchall()

    ColumnNames = [description[0] for description in ScoresDataBaseProcessor.Cursor.description]

    with open(CsvFile, 'w', newline='') as File:
        CsvWriter = csv.writer(File)

        CsvWriter.writerow(ColumnNames)

        CsvWriter.writerows(Rows)

        # Write the global average score
        CsvWriter.writerow(["Average Score", CalculateAverageScores()])

    
def DirectlyInsert(Student,Score):

    try:
        InsertStudentsandScores(Student,Score)
        OutputFile = r"E:\2024-Project-score-manager-github\v1\Tests\ScoreResult.csv"
        # PeopleScores = MergeStudentsAndScores(Students, Scores)
        # RankedPeople = RankPeople(PeopleScores)
        # WritingResultsToDatabase(RankedPeople)
        InsertStudentsAndPasswords()
        # Export results to CSV
        ExportResultsToCSV(Constant.OutputFile)

        print(f"Ranking results have been written to {OutputFile}")
        print("Data has been successfully inserted into the SQLite database.")
    
    except Exception as E:
        print(f"An error occurred: {E}")
    



def main(Filepath):
    # Open the database
    open_database()

    try:
        File = Filepath
        OutputFile = r"E:\2024-Project-score-manager-github\v1\Tests\ScoreResult.csv"

        # Processing steps
        Students,Scores = ReadStudent(File)
        PeopleScores = MergeStudentsAndScores(Students, Scores)
        
        RankedPeople = RankPeople(PeopleScores)
        AverageScore = CalculateAverageScores()
        WritingResultsToDatabase(RankedPeople)
        InsertStudentsAndPasswords()

        # Export results to CSV
        ExportResultsToCSV(Constant.OutputFile)

        print(f"Ranking results have been written to {OutputFile}")
        print("Data has been successfully inserted into the SQLite database.")
    
    except Exception as E:
        print(f"An error occurred: {E}")
    
   
