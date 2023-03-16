import requests

url = 'http://localhost:3000/oauth/api/user_info'
myobj = {'auth_code': 'b156efa19a579e1be66a551530234513c53011cef2914bc713c123eab86084d6', 'client_id': '64008b39-9a69-4a65-b54d-bff3081cb626', 'client_secret': '86db2661-4202-466d-b43b-0bc31a470f29'}

x = requests.post(url, json = myobj)

#print the response text (the content of the requested file):

print(x.text)
