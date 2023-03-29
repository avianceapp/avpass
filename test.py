import requests

url = 'http://localhost:3000/oauth/api/user_info'
myobj = {'auth_code': 'a8dfa86973cac287e32fd64dfc14017e186f0eda257ea97e150fe24ba39b2941', 'client_id': '64008b39-9a69-4a65-b54d-bff3081cb626', 'client_secret': '271367673dc870f17dd253a8792b9d9b3ff76d252608d0906ac917e53ccfbaf3'}

x = requests.post(url, json = myobj)

#print the response text (the content of the requested file):

print(x.text)
