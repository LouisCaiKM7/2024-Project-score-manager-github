import csv
import Constant
import sqlite3

Conn = sqlite3.connect(Constant.DatabaseFile, check_same_thread=False)
Cursor = Conn.cursor()
def Excecuter():
    Cursor.execute('''
    CREATE TABLE IF NOT EXISTS Students (
        id TEXT PRIMARY KEY,
        Name TEXT
    )
    ''')

    Cursor.execute('''
    CREATE TABLE IF NOT EXISTS Scores (
        id TEXT,
        Score INTEGER,
        FOREIGN KEY (id) REFERENCES Students(id)
    )
    ''')

    Cursor.execute('''
    CREATE TABLE IF NOT EXISTS Results (
        Name TEXT,
        Score INTEGER
    )
    ''')

def InsertStudents(CsvFile):
    with open(CsvFile, 'r') as file:
        CsvReader = csv.reader(file)
        next(CsvReader)  
        for Row in CsvReader:
            id, Name = Row
            Cursor.execute("INSERT OR IGNORE INTO Students (id, Name) VALUES (?, ?)", (id, Name))

def InsertScores(CsvFile):
    with open(CsvFile, 'r') as file:
        CsvReader = csv.reader(file)
        next(CsvReader)  
        for Row in CsvReader:
            id, Score = Row
            Cursor.execute("INSERT OR IGNORE INTO Scores (id, Score) VALUES (?, ?)", (id, int(Score)))


# def InsertResults(CsvFile):
#     with open(CsvFile, 'r') as file:
#         CsvReader = csv.reader(file)
#         for Row in CsvReader:
#             if len(Row) != 2:
#                 continue
#             Name, Score = Row
#             Cursor.execute("INSERT INTO Results (Name, Score) VALUES (?, ?)", (Name, Score))