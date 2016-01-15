Before running the script do

1. Install  Google APIs Client Library for Python
Ref: https://developers.google.com/api-client-library/python/start/installation

Use pip or setuptools to manage your installation (you might need to run sudo first):

pip (preferred):
$ pip install --upgrade google-api-python-client
      
Setuptools: Use the easy_install tool included in the setuptools package:
$ easy_install --upgrade google-api-python-client

Windows: Run above command in powershell after python and pip is installed.

2. Insert Authorized redirect URIs: 
http://localhost:8080/ 
in youtube OAuth 2.0 Client ID for Web application in Google console.

3. Download JSON file from Google console for the client ID and save in this folder. Rename JSON file with following name: client_secrets.json
