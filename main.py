# main.py
import http.server
import socketserver
import os
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PORT = 8000
DIRECTORY = "frontend"

os.chdir(DIRECTORY)

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving frontend at http://localhost:{PORT}")
    httpd.serve_forever()