import requests
import json

with open('soc', 'r') as file:
    params = json.loads(file.read())
r = requests.post('https://soc-ege.sdamgia.ru/test?a=generate',params = params)
print(r.url)
