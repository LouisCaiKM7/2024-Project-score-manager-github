import csv
import os
import Constant
import ScoresDataBaseProcessor
import sqlite3
import UsersDatabaseProcessor
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify

GlobalScore = {}

ScoresDataBaseProcessor.Excecuter()


def open_database():
    ScoresDataBaseProcessor.Conn = sqlite3.connect(Constant.DatabaseFile, check_same_thread=False)
    ScoresDataBaseProcessor.Cursor = ScoresDataBaseProcessor.Conn.cursor()

def close_database():
    if ScoresDataBaseProcessor.Conn:
        ScoresDataBaseProcessor.Conn.commit()  # Ensure all changes are committed
        ScoresDataBaseProcessor.Conn.close()


def MergeStudentsAndScores():
    ScoresDataBaseProcessor.Cursor.execute('''
        SELECT Students.Name, Scores.Score 
        FROM Students 
        JOIN Scores ON Students.id = Scores.id
    ''')
    PeopleScores = ScoresDataBaseProcessor.Cursor.fetchall()

    for name, score in PeopleScores:
        GlobalScore[name] = score

    return PeopleScores

def InsertStudentsAndPasswords(): 
    # Fetch student names from the Scores database
    ScoresDataBaseProcessor.Cursor.execute("SELECT Name FROM Students")
    Peopleid = ScoresDataBaseProcessor.Cursor.fetchall()
    
    # Print fetched data
    print(Peopleid)
    
    for person in Peopleid:
        # 'person' is a tuple, so we need to get the first element (the name)
        name = person[0]
        
        # Check if the id (name) already exists in the Users database
        UsersDatabaseProcessor.Cur.execute("SELECT id FROM Students WHERE id = ?", (name,))
        existing_record = UsersDatabaseProcessor.Cur.fetchone()
        
        # If no existing record is found, insert the new student
        if not existing_record:
            UsersDatabaseProcessor.Cur.execute(
                "INSERT INTO Students (id, password) VALUES (?, ?)",
                (name, generate_password_hash(name))
            )
        else:
            print(f"Skipping {name}, already exists.")

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

    
def DirectlyInsert():

    try:
        OutputFile = r"E:\2024-Project-score-manager-github\v1\Tests\ScoreResult.csv"
        PeopleScores = MergeStudentsAndScores()
        RankedPeople = RankPeople(PeopleScores)
        WritingResultsToDatabase(RankedPeople)

        # Export results to CSV
        ExportResultsToCSV(Constant.OutputFile)

        print(f"Ranking results have been written to {OutputFile}")
        print("Data has been successfully inserted into the SQLite database.")
    
    except Exception as E:
        print(f"An error occurred: {E}")
    
    finally:
        # Ensure the database is closed after processing
        close_database()



def main(StudentFilePath, ScoreFilePath):
    # Open the database
    open_database()

    try:
        StudentsFile = StudentFilePath
        ScoresFile = ScoreFilePath
        OutputFile = r"E:\2024-Project-score-manager-github\v1\Tests\ScoreResult.csv"
    
        # Insert data into the database
        ScoresDataBaseProcessor.InsertStudents(StudentsFile)
        ScoresDataBaseProcessor.InsertScores(ScoresFile)
        PeopleScores = MergeStudentsAndScores()
        RankedPeople = RankPeople(PeopleScores)
        WritingResultsToDatabase(RankedPeople)
        InsertStudentsAndPasswords()

        # Export results to CSV
        ExportResultsToCSV(Constant.OutputFile)

        print(f"Ranking results have been written to {OutputFile}")
        print("Data has been successfully inserted into the SQLite database.")
    
    except Exception as E:
        print(f"An error occurred: {E}")
    
    finally:
        # Ensure the database is closed after processing
        close_database()
