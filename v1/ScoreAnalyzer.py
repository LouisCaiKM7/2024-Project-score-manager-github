import Constant
def ReadScores(FileName):
    PeopleScores = []

    with open(FileName, 'r') as File:
        for Line in File:
            Line = Line.strip()

            if not Line:
                continue

            try:
                Name, Score = Line.split()
                PeopleScores.append((Name, int(Score)))
            except ValueError:
                print(f"Skipping Line due to format issue: {Line}")

    return PeopleScores

def CalculateAverageScores(PeopleScores):
    if not PeopleScores:
        return 0  # Avoid division by zero if there are no scores
    AverageScore = sum(score for _, score in PeopleScores) / len(PeopleScores)
    return AverageScore

def RankPeople(PeopleScores):
    RankedPeople = sorted(PeopleScores, key=lambda x: x[1], reverse=True)
    return RankedPeople

def WritingResults(RankedPeople, AverageScore, OutputFile):
    with open(OutputFile, 'w') as File:
        for Rank, (Name, Score) in enumerate(RankedPeople, start=1):
            File.write(f"{Name} {Score}\n")
        File.write(f"\nAverage Score: {AverageScore:.2f}\n")

InputFile = Constant.InputFile
OutputFile = Constant.OutputFile
PeopleScores = ReadScores(InputFile)

RankedPeople = RankPeople(PeopleScores)

AverageScore = CalculateAverageScores(PeopleScores)


WritingResults(RankedPeople, AverageScore, OutputFile)

print(f"Ranking results have been written to {OutputFile}")

#demo