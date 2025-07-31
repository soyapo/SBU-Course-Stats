import os
import json
from Classes.Student import Student

DATA_PATH = os.getcwd() + "\\App\\Data\\data.json"

def ModifyJSON(student):
    # Load existing data
    with open (DATA_PATH, "r") as r:
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
