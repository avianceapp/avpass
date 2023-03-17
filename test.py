import requests

url = 'http://localhost:3000/oauth/api/user_info'
myobj = {'auth_code': '4cd791e05cd5b64e4dd9d9791826e378e0633757f870ec9b683ae2b0bd2d737d', 'client_id': 'b897adf3-d8c2-4e9f-9f3e-e049bfe9ab88', 'client_secret': '976f9663b6edddfc675907ae2013f0dad17c5127c61882a5e4c10b116b7c3c94'}

x = requests.post(url, json = myobj)

#print the response text (the content of the requested file):

print(x.text)
