import os
import json
from Classes.Student import Student

DATA_PATH = os.getcwd() + "/data/data.json"

def ModifyJSON(student):
    # Load existing data (a fresh scrape starts with no file)
    EXISTING_DATA = []
    if os.path.exists(DATA_PATH):
        with open (DATA_PATH, "r", encoding="utf-8") as r:
            EXISTING_DATA = json.load(r)

    # Check if the student already exists, if so update their information
    exists = 0
    for i, entry in enumerate(EXISTING_DATA):
        if entry.get("SBUID") == student["SBUID"]:
            EXISTING_DATA[i] = student
            exists = 1
            break

    # If the student doesn't exist, add them to the list
    if not exists: 
        EXISTING_DATA.append(student)

    # Save the updated data back to the JSON file
    with open(DATA_PATH, "w") as w:
        json.dump(EXISTING_DATA, w, indent = 4)

# Stamp each student's semester-in-program as of (currentYear, semester),
# e.g. addSemester(405, 1, ...) for the 1405 first-semester snapshot
def addSemester(currentYear, semester, path=DATA_PATH):
    with open (path, "r", encoding="utf-8") as r:
        EXISTING_DATA = json.load(r)
    
    for student in EXISTING_DATA:  # Direct iteration
        studentYear = student["Year"]
        studentYear += 300 if studentYear < 100 else 0
        totalSemester = 2 * (currentYear - studentYear) + semester
        student["Semester"] = totalSemester

    with open(path, "w", encoding="utf-8") as w:
        json.dump(EXISTING_DATA, w, indent = 4)

def correctDegree(path=DATA_PATH):
    with open (path, "r", encoding="utf-8") as r:
        data = json.load(r)

    for student in data:
        student["Degree"] = int(student["SBUID"][-6:-5])

    with open(path, "w", encoding="utf-8") as w:
        json.dump(data, w, indent = 4)

# Run directly (not on import, since Spider.py imports this module)
if __name__ == "__main__":
    addSemester(405, 1, os.getcwd() + "/data/22-4051.json")