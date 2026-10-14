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
    
    # returns None on a network error so the caller can skip this ID
    def request(self):
        try:
            response = requests.post(url=self.url, data=self.data, timeout=30)
        except requests.RequestException:
            return None
        return response
