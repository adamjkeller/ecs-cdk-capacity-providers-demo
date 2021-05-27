#!/usr/bin/env python3

from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def index():
    return f'{{ "OS_Architecture": "{os.uname().machine}" }}'

if __name__ == '__main__':
    app().run(host='0.0.0.0')
