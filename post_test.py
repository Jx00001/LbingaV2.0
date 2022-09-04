import requests
from time import sleep

data = 0

for i in range(1, 2320):
    r = requests.post('http://127.0.0.1/api/in', 
    json = {
    "key": "test",
    "what": "xp",
    "UserID": 655529290405904394,
    "data": data
    })

    print(f"Status: {r.status_code}, Response: {r.json()['response']}")
    data += 10
