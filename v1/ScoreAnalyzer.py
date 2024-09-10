import csv
import os
import Constant
import SqliteFile
import sqlite3
from flask import Flask, request, jsonify

GlobalScore = {}

SqliteFile.Excecuter()


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
            GlobalScore[Name] = Scores[StudentID]

    return PeopleScores

def CalculateAverageScores():
    if not GlobalScore:
        return 0  # No scores to calculate
    AverageScore = "{:.2f}".format(sum(GlobalScore.values()) / len(GlobalScore))
    return AverageScore

def RankPeople(PeopleScores):
    RankedPeople = sorted(PeopleScores, key=lambda x: x[1], reverse=True) 
    return RankedPeople


def WritingResultsToDatabase(RankedPeople):
    for Name, Score in RankedPeople:
        SqliteFile.Cursor.execute("INSERT INTO Results (Name, Score) VALUES (?, ?)", (Name, Score))

    


def ExportResultsToCSV(CsvFile):
    
    SqliteFile.Cursor.execute("SELECT Name, Score FROM Results")
 
    Rows = SqliteFile.Cursor.fetchall()

    ColumnNames = [description[0] for description in SqliteFile.Cursor.description]

    with open(CsvFile, 'w', newline='') as File:
        CsvWriter = csv.writer(File)

        CsvWriter.writerow(ColumnNames)

        CsvWriter.writerows(Rows)

        # Write the global average score
        CsvWriter.writerow(["Average Score", CalculateAverageScores()])

    
        

    

def main(StudentFilePath,ScoreFilePath):
    StudentsFile =StudentFilePath
    ScoresFile = ScoreFilePath
    OutputFile = "ScoreResult.csv"


    Students = ReadStudents(StudentsFile)
    Scores = ReadScores(ScoresFile)

    PeopleScores = MergeStudentsAndScores(Students, Scores)

    RankedPeople = RankPeople(PeopleScores)

    AverageScore = CalculateAverageScores()

# WritingResults(RankedPeople, AverageScore, OutputFile)

    print(f"Ranking results have been written to {OutputFile}")
    # SqliteFile.Conn = sqlite3.connect(Constant.DatabaseFile, check_same_thread=False)
    SqliteFile.InsertStudents(StudentsFile)
    SqliteFile.InsertScores(ScoresFile)
    WritingResultsToDatabase(RankedPeople)
    ExportResultsToCSV(Constant.OutputFile)

    SqliteFile.Conn.commit()
    # SqliteFile.Conn.commit()
    

    print("Data has been successfully inserted into the SQLite database.")


