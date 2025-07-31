import requests

class DataRequest:
    # SBU's API endpoint
    url = "https://vu.sbu.ac.ir/class/course.list.php"
    data = {}
    
    def __init__(self, SBUID):
        # the request only requires a username key, with the value being the SBU ID
        self.data = {
            "username": SBUID
        }
    
    def request(self):
        try:
            response = requests.post(url=self.url, data=self.data)
        except:
            return 0
        return response
