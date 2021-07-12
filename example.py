import os
from homeassistant_api import Client


url = os.getenv('HOMEASSISTANT_API_ENDPOINT')  # http://localhost:8123/api/
token = os.getenv('HOMEASSISTANT_API_TOKEN')  # ey816najgfjassf...


client = Client(url, token)  # Creates the object uses to interact with the api
# In init it checks to see if the api is running by sending a check request
# If successful it also validates that the configuration.yml on you rhomeasistant is formatted correctly

domains = client.get_domains()

service = domains['notify'].services['mobile_app_nathan_s_iphone']

resp = service.trigger(
    message='The quick brown fox jumped over the lazy doge.',
    title='Hello there!'
)

