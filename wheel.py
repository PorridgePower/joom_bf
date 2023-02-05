import requests
import re
import json
import time
import random
import string

MAIN_URL = "https://www.joom.com/ru"
API_URL = "https://api.joom.com/1.1/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"

HEADERS = {"authority": "www.joom.com",
           "user-agent": USER_AGENT,
           'Connection': 'close'}


def generate_api_token():
    return ''.join(random.choices(string.ascii_letters+string.digits, k=32))


while (True):
    s = requests.session()
    s.headers = HEADERS
    s.cookies.clear()
    resp = s.get(MAIN_URL)

    renderingConfigId = re.search(
        r"window.__renderingConfig={\"id\":\"(.*)\",\"option\":\"server\"};", resp.text).group(1)

    print("GET hydrate")
    data = {"language": "ru", "renderingId": renderingConfigId}
    resp = s.get(
        url=f"https://www.joom.com/tokens/hydrate", params=data)
    clientData = json.loads(resp.text)

    print("POST upgrade")
    s.headers["x-rendering-id"] = renderingConfigId
    s.headers["x-api-token"] = generate_api_token()
    data = {"reason": {"type": "restrictedEndpoint",
                       "endpoint": "/rewardWheel/get"}}
    resp = s.post(
        url="https://www.joom.com/tokens/upgrade?language=ru-RU", json=data)

    clientData = json.loads(resp.text)
    print(clientData["payload"]["accessToken"])

    print("POST rewardWheel/get")
    s.headers["authorization"] = "Bearer " + \
        clientData["payload"]["accessToken"]
    resp = s.post(url=f"{API_URL}rewardWheel/get?language=ru-RU")
    wheelData = json.loads(resp.text)
    wheelId = wheelData["payload"]["id"]

    print("POST rewardWheel/activate")
    resp = s.post(
        url=f"{API_URL}rewardWheel/{wheelId}/activate?language=ru-RU")
    rewardData = json.loads(resp.text)

    winningSectionId = rewardData["payload"]["wheel"]["state"]["payload"]["activated"]["reward"]["winningSectionId"]
    if winningSectionId == 6:
        print(s.cookies.get_dict())
        break
    s.close()

    time.sleep(10)
