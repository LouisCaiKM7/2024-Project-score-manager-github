import csv
import Constant
import SqliteFile
import sqlite3



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

    return PeopleScores

def CalculateAverageScores(PeopleScores):
    if not PeopleScores:
        return 0 
    AverageScore = "{:.2f}".format(sum(Score for _, Score in PeopleScores) / len(PeopleScores))
    return AverageScore

def RankPeople(PeopleScores):
    RankedPeople = sorted(PeopleScores, key=lambda x: x[1], reverse=True) 
    return RankedPeople


def WritingResultsToDatabase(RankedPeople, AverageScore):
    for Name, Score in RankedPeople:
        SqliteFile.Cursor.execute("INSERT INTO Results (Name, Score) VALUES (?, ?)", (Name, Score))

    SqliteFile.Cursor.execute("INSERT INTO Results (Name, Score) VALUES (?, ?)", ("Average Score",AverageScore))


def ExportResultsToCSV(CsvFile):
    
    SqliteFile.Cursor.execute("SELECT Name, Score FROM Results")
 
    Rows = SqliteFile.Cursor.fetchall()

    ColumnNames = [description[0] for description in SqliteFile.Cursor.description]

    with open(CsvFile, 'w', newline='') as File:
        CsvWriter = csv.writer(File)

        CsvWriter.writerow(ColumnNames)

        CsvWriter.writerows(Rows)

    


StudentsFile = Constant.StudentsFile 
ScoresFile = Constant.ScoresFile 
OutputFile = Constant.OutputFile 
DatabaseFile = Constant.DatabaseFile


Students = ReadStudents(StudentsFile)
Scores = ReadScores(ScoresFile)

PeopleScores = MergeStudentsAndScores(Students, Scores)

RankedPeople = RankPeople(PeopleScores)

AverageScore = CalculateAverageScores(PeopleScores)

# WritingResults(RankedPeople, AverageScore, OutputFile)

print(f"Ranking results have been written to {OutputFile}")

SqliteFile.InsertStudents(Constant.StudentsFile)
SqliteFile.InsertScores(Constant.ScoresFile)
WritingResultsToDatabase(RankedPeople, AverageScore)
ExportResultsToCSV(Constant.OutputFile)


SqliteFile.Conn.commit()
SqliteFile.Conn.close()

print("Data has been successfully inserted into the SQLite database.")
