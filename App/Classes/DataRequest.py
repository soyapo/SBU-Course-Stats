import requests

class DataRequest:
    url = "https://vu.sbu.ac.ir/class/course.list.php"
    data = {}

    def __init__(self, SBUID):
        self.data = {
            "username": SBUID
        }
    
    def request(self):
        try:
            response = requests.post(url=self.url, data=self.data)
        except:
            return 0
        return response
