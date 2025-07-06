import requests

TOKEN = '7914391496:AAE3H3dbB1Bot3l1o74j2eNaPXRjdTCziJY'
URL = f'https://api.telegram.org/bot{TOKEN}/getUpdates'

response = requests.get(URL)
print(response.json())
