#!/usr/bin/python

# Examining HTTP request/response using the 'requests' module

# 1. Set up a simple 2-node Mininet network ('sudo -E mn')
# 2. Run a web server on node h2 ('python -m http.server 8000')
# 3. Run this program on node h1

# Import the requests module. See https://docs.python-requests.org/en/latest/
import requests
from pprint import pprint

# Send an HTTP GET request
r = requests.get('http://10.0.0.2:8000/')

print('\nURL:')
print(r.url)

# Display the headers sent in the request message to the server
print('\nRequest headers:')
pprint(dict(r.request.headers))

# Display the status code returned from the server
print('\nStatus code: {} {}'.format(r.status_code, r.reason))

# Display the headers in the response message from the server
print('\nResponse headers:')
pprint(dict(r.headers))

# Display the content returned from the server
# r.content is a byte array, so we encode it as text
print('\nContent:')
print(r.content.decode())
