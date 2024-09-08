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
    AverageScore = sum(Score for _, Score in PeopleScores) / len(PeopleScores)
    return AverageScore

def RankPeople(PeopleScores):
    RankedPeople = sorted(PeopleScores, key=lambda x: x[1], reverse=True) 
    return RankedPeople

def WritingResults(RankedPeople, AverageScore, OutputFile):
    with open(OutputFile, 'w') as File:
        for Name, Score in RankedPeople:
            File.write(f"{Name},{Score}\n")
        
        File.write(f"\nAverage Score,{AverageScore:.2f}\n")


StudentsFile = Constant.StudentsFile 
ScoresFile = Constant.ScoresFile 
OutputFile = Constant.OutputFile 


Students = ReadStudents(StudentsFile)
Scores = ReadScores(ScoresFile)

PeopleScores = MergeStudentsAndScores(Students, Scores)

RankedPeople = RankPeople(PeopleScores)

AverageScore = CalculateAverageScores(PeopleScores)

WritingResults(RankedPeople, AverageScore, OutputFile)

print(f"Ranking results have been written to {OutputFile}")

SqliteFile.InsertStudents(Constant.StudentsFile)
SqliteFile.InsertScores(Constant.ScoresFile)
SqliteFile.InsertResults(Constant.OutputFile)

SqliteFile.Conn.commit()
SqliteFile.Conn.close()

print("Data has been successfully inserted into the SQLite database.")








# import sqlite3
# import csv
# import Constant

# # Connect to SQLite database (creates a new database file if it doesn't exist)
# Conn = sqlite3.Connect('Scores_database.db')
# Cursor = Conn.Cursor()

# # Create Students table
# Cursor.execute('''
# CREATE TABLE IF NOT EXISTS Students (
#     id TEXT PRIMARY KEY,
#     Name TEXT
# )
# ''')

# # Create Scores table
# Cursor.execute('''
# CREATE TABLE IF NOT EXISTS Scores (
#     id TEXT,
#     Score INTEGER,
#     FOREIGN KEY (id) REFERENCES Students(id)
# )
# ''')

# # Create Results table (for ranking and average Score)
# Cursor.execute('''
# CREATE TABLE IF NOT EXISTS Results (
#     Name TEXT,
#     Score INTEGER
# )
# ''')

# # Function to insert data from CSV into the Students table
# def InsertStudents(csv_file):
#     with open(csv_file, 'r') as file:
#         CsvReader = csv.reader(file)
#         next(CsvReader)  # Skip header
#         for Row in CsvReader:
#             id, Name = Row
#             Cursor.execute("INSERT INTO Students (id, Name) VALUES (?, ?)", (id, Name))

# # Function to insert data from CSV into the Scores table
# def InsertScores(csv_file):
#     with open(csv_file, 'r') as file:
#         CsvReader = csv.reader(file)
#         next(CsvReader)  # Skip header
#         for Row in CsvReader:
#             id, Score = Row
#             Cursor.execute("INSERT INTO Scores (id, Score) VALUES (?, ?)", (id, int(Score)))

# # Function to insert data into Results table (use the already ranked data)
# def InsertResults(csv_file):
#     with open(csv_file, 'r') as file:
#         CsvReader = csv.reader(file)
#         next(CsvReader)  # Skip header
#         for Row in CsvReader:
#             Name, Score = Row
#             Cursor.execute("INSERT INTO Results (Name, Score) VALUES (?, ?)", (Name, int(Score)))

# # Insert data from the CSV files
# InsertStudents(Constant.StudentsFile)
# InsertScores(Constant.ScoresFile)
# InsertResults(Constant.OutputFile)

# # Commit the changes and close the Connection
# Conn.commit()
# Conn.close()

# print("Data has been successfully inserted into the SQLite database.")
