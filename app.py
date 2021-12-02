#!/usr/bin/env python3
# app.py
# Task Master Tutorial Flask App Main
# v0.5.0
# pylint: disable=too-few-public-methods

"""Task Master Flask tutorial web application allows to maintain
a list of tasks using respective CRUD operations
(create, read, update, delete)."""


import os

from datetime import datetime
from typing import cast

from flask import Flask, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy

# See typings/__init__.py for more information
from typings.sql_alchemy import SQLAlchemy as SQLAlchemyStub


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Required for session support
app.secret_key = os.environ['SESSION_KEY']

# Linter hell, see above
db = cast(SQLAlchemyStub, SQLAlchemy(app))
Model = db.Model


class Task(Model):
    """This class represents a task, ie. an item on a to-do list."""
    __tablename__ = 'tasks'

    id: int = db.Column(db.Integer, primary_key=True)
    content: str = db.Column(db.String(512), nullable=False)
    created: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    completed: bool = db.Column(db.Boolean, default=False)


@app.route('/')
def index():
    """Flask controller for the root/index endpoint (/)
    of the web application.
    """
    message = session.pop('message', default='')

    tasks = []

    try:
        tasks = db.session.query(Task).all()
    except Exception as ex:
        '<br>'.join([message, f'Database error: {ex}'])

    return render_template('index.html', message=message, tasks=tasks)


@app.route('/add', methods=['POST'])
def add():
    """Add a task to the database or yield an error."""
    task_content = request.form.get('content', default='').strip()

    message = ''

    if task_content:
        try:
            task = Task()
            task.content = task_content
            db.session.add(task)
            db.session.commit()
            message = 'Task added successfully.'
        except Exception as ex:
            message = f'Error adding task: {ex}'
    else:
        message = 'Task description must not be empty.'

    session['message'] = message
    return redirect('/')


if __name__ == '__main__':
    """Main entry point for the application."""
    app.run(debug=True)
