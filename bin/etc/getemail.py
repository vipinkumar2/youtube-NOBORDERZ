import requests

def generate_gmail(ID: int):
  
  # access the API
  url = "https://temp-gmail.p.rapidapi.com/get"
  querystring = {"id":ID,"type":"alias"}
  headers = {
    'x-rapidapi-host': "temp-gmail.p.rapidapi.com",
    'x-rapidapi-key': "6482cb12c2msh662dfee80477fd6p1495f7jsn8ee1247ec672"
    }
  
  # send a request to the API
  response = requests.request("GET", url, headers=headers, params=querystring)
  
  # convert the response to JSON format 
  json_response = response.json()
  print(json_response)
  # get gmail address
  gmail = json_response['items']['username']
  # get gmail password
  password = json_response['items']['key']

  print('Gmail address: %s' % str(gmail))
  print('Password: %s' % str(password))
  
generate_gmail(3)