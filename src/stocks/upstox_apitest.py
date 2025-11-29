import requests

url = 'https://api.upstox.com/v2/user/profile'
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiJIVzUyMTMiLCJqdGkiOiI2OTJiMTYxYmIzNGEzMTEzNGI4Njg4MjUiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2NDQzMTM4NywiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzY0NDUzNjAwfQ.vghdYoodvEACrrYa9EU6yF6A98EnNdJ1ovNjkPkOYok'
}
response = requests.get(url, headers=headers)

print(response.status_code)
print(response.json())