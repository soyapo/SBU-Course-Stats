from time import sleep
from bs4 import BeautifulSoup # for html parsing

# Local class imports
from JSONModifier import *
from Classes.Student import Student
from Classes.DataRequest import DataRequest


# Base Info
degree = 2 # 2 for bachelor
faculty = 22 # 22 for Maths, replace with your desired faculty code 

IdStrings = [f"{i:03}" for i in range(221, 240)] # includes all strings from 001 to 220 for student IDs. the maximum yet seen irl is 221.

for year in range(403, 404): # modify to your desired entry years
    for id in IdStrings:
        SBUID = str(year) + str(degree) + str(faculty) + id 
        
        # Making a POST request and saving the result in ResponseHTML
        request = DataRequest(SBUID)
        ResponseHTML = request.request()

        # HTML parsing
        soup = BeautifulSoup(ResponseHTML.text, "html.parser")

        exists = 0
        CourseList = []
        ListItems = soup.find_all("li", class_="list-group-item")

        for item in ListItems:
            aTag = item.find("a")
            if aTag:
                exists = 1        
                CourseList.append(aTag.get_text(strip=True)[:-16]) # Removing course codes from the end of the string

        # creating an Student instance with the scraped data in case of existance
        if exists:
            student = Student(SBUID, year, degree, faculty, "", CourseList)
            ModifyJSON(student.Dictator())
        
        sleep(0.05)