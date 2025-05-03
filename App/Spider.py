from DataRequest import DataRequest
from Student import Student
from bs4 import BeautifulSoup # for html parsing

# Base Info
year = 403 # Entry year of the student
degree = 2 # 2 for bachelor
faculty = 16 # 22 for Maths, replace with your desired faculty code 
CourseList = []

# Making a POST request and saving the result in ResponseHTML
request = DataRequest(str(year) + str(degree) + str(faculty) + "009")
ResponseHTML = request.request()

# HTML parsing
soup = BeautifulSoup(ResponseHTML.text, "html.parser")

ListItems = soup.find_all("li", class_="list-group-item")
for item in ListItems:
    aTag = item.find("a")
    if aTag:        
         CourseList.append(aTag.get_text(strip=True)[:-16]) # Removing course codes from the end of the string

# creating an Student instance with the scraped data
student = Student("403222214", year, degree, faculty, "", CourseList)
print(student)

