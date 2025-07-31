# Student data scheme to be used for scraping and analyzing data
class Student:
    def __init__(self, SBUID, Year, Degree, Faculty, Major, CourseList=None):
        self.SBUID = SBUID
        self.Year = Year
        self.Degree = Degree
        self.Faculty = Faculty
        self.Major = Major
        self.CourseList = CourseList if CourseList is not None else []
    
    def __str__(self):
        return (
            f"Student ID: {self.SBUID}\n"
            f"Entry Year: {self.Year}\n"
            f"Degree: {self.Degree}\n"
            f"Faculty: {self.Faculty}\n"
            f"Major: {self.Major if self.Major else 'N/A'}\n"
            f"Courses Enrolled: {', '.join(self.CourseList) if self.CourseList else 'None'}"
        )
    
    # Convert the student instance into a dictionary
    def Dictator(self):
        return {
            "SBUID": self.SBUID,
            "Year": self.Year,
            "Degree": self.Degree,
            "Faculty": self.Faculty,
            "Major": self.Major,
            "CourseList": self.CourseList
        }