import csv
import os
import Constant
import ScoresDataBaseProcessor
import sqlite3
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

def ReadStudents(FileName):
    Students = {}

    with open(FileName, 'r') as File:
        CsvReader = csv.reader(File)
        next(CsvReader) 

        for Row in CsvReader:
            Name, StudentID = Row
            Students[StudentID] = Name 

    return Students

def ReadScores(FileName):
    Scores = {}

    with open(FileName, 'r') as File:
        CsvReader = csv.reader(File)
        next(CsvReader)  

        for Row in CsvReader:
            StudentID, Score = Row
            Scores[StudentID] = int(Score) 

    return Scores

def MergeStudentsAndScores(Students, Scores):
    PeopleScores = []

    for StudentID, Name in Students.items():
        if StudentID in Scores:
            PeopleScores.append((Name, Scores[StudentID]))
            

    return PeopleScores

def CalculateAverageScores():
    ScoresDataBaseProcessor.Cursor.execute("SELECT Score FROM Results")
    Scores = ScoresDataBaseProcessor.Cursor.fetchall()

    if not Scores:
        return 0  # No scores to calculate

    # Extract the scores (assuming they are in tuple format from fetchall)
    TotalScores = [score[0] for score in Scores if isinstance(score[0], int)]  # Filter to avoid non-integer scores

    # Calculate the average
    AverageScore = "{:.2f}".format(sum(TotalScores) / len(TotalScores)) if TotalScores else 0
    return AverageScore

def RankPeople(PeopleScores):
    RankedPeople = sorted(PeopleScores, key=lambda x: x[1], reverse=True) 
    return RankedPeople


def WritingResultsToDatabase(RankedPeople):
    for Name, Score in RankedPeople:
        ScoresDataBaseProcessor.Cursor.execute("INSERT INTO Results (Name, Score) VALUES (?, ?)", (Name, Score))

    


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

    
        

def main(StudentFilePath, ScoreFilePath):
    # Open the database
    open_database()

    try:
        StudentsFile = StudentFilePath
        ScoresFile = ScoreFilePath
        OutputFile = "ScoreResult.csv"

        # Processing steps
        Students = ReadStudents(StudentsFile)
        Scores = ReadScores(ScoresFile)
        PeopleScores = MergeStudentsAndScores(Students, Scores)
        RankedPeople = RankPeople(PeopleScores)
        AverageScore = CalculateAverageScores()

        # Insert data into the database
        ScoresDataBaseProcessor.InsertStudents(StudentsFile)
        ScoresDataBaseProcessor.InsertScores(ScoresFile)
        WritingResultsToDatabase(RankedPeople)

        # Export results to CSV
        ExportResultsToCSV(Constant.OutputFile)

        print(f"Ranking results have been written to {OutputFile}")
        print("Data has been successfully inserted into the SQLite database.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Ensure the database is closed after processing
        close_database()
