#!/usr/bin/env python3
# app.py
# Task Master Tutorial Flask App Main
# v0.4.0

"""Task Master Flask tutorial web application allows to maintain
a list of tasks using respective CRUD operations
(create, read, update, delete)."""


from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def index():
    """Flask controller for the root/index endpoint (/)
    of the web application.
    """
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
