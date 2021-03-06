#!/usr/bin/env python3
# app.py
# Task Master Tutorial Flask App Main
# pylint: disable=too-few-public-methods

"""Task Master Flask tutorial web application allows to maintain
a list of tasks using respective CRUD operations
(create, read, update, delete)."""

__version__ = '0.9.1'

__author__ = 'Markus M. Egger'
__credits__ = ['Jake Rieger', 'WilsonPhooYK']
__copyright__ = 'Copyright (C) 2021 by Markus M. Egger'
__license__ = 'BSD-3'
__status__ = 'Development'


import os

from datetime import datetime
from pathlib import Path
from typing import cast

from flask import Flask, render_template, redirect, request, session, url_for
from flask_sqlalchemy import SQLAlchemy

# See typings/__init__.py for more information
from typings.sql_alchemy import SQLAlchemy as SQLAlchemyStub


TASK_LIMIT = 10


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
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

    def __init__(self, content: str) -> None:
        super().__init__()
        self.content = content

    def __repr__(self):
        return f'<Task {self.id}>'


@app.route('/')
def index():
    """Main (root, index) endpoint of the application displaying
    the list of tasks and possible interactions.
    """
    if not session.get('DATABASE_SETUP', default=False):
        return redirect(url_for('setup'))

    message = session.pop('message', default='')

    tasks = []

    try:
        tasks = Task.query.order_by(Task.created).all()
    except Exception as ex:
        '<br>'.join([message, f'Database error: {ex}'])

    return render_template('index.html', message=message, tasks=tasks)


@app.route('/setup')
def setup():
    """Initializes the SQLite database based on a session
    variable or the "force" query parameter.
    """
    force: bool = request.args.get('force', None) is not None
    
    if force or not session.get('DATABASE_SETUP', default=False):
        # Prevent an endless redirection cycle on error
        # regardless of the result of create_all()
        session['DATABASE_SETUP'] = True
        try:
            db.create_all()
            session['message'] = 'Database created.'
        except Exception as ex:
            session['message'] = f'Database/table creation error: {ex}'
    
    return redirect(url_for('index'))


@app.route('/add', methods=['POST'])
def add():
    """Add a task to the database or yield an error."""
    task_content = request.form.get('content', default='').strip()

    message = ''

    if Task.query.count() >= TASK_LIMIT:
        message = f'Sorry, no more than {TASK_LIMIT} tasks allowed.'
    else:
        if task_content:
            try:
                task = Task(content=task_content)
                db.session.add(task)
                db.session.commit()
                message = 'Task added successfully.'
            except Exception as ex:
                message = f'Error adding task: {ex}'
        else:
            message = 'Task description must not be empty.'

    session['message'] = message
    return redirect(url_for('index'))


@app.route('/remove/<int:id>')
def remove(id: int):
    """Remove an existing task or yield an error."""
    task_to_remove = Task.query.get_or_404(id)

    try:
        db.session.delete(task_to_remove)
        db.session.commit()
        message = 'Task removed successfully.'
    except Exception as ex:
        message = f'Error removing task: {ex}'
    
    session['message'] = message
    return redirect(url_for('index'))


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id: int):
    """Update the description of an existing task.
    
    The new task description must neither be empty nor
    identical to the old one.
    """
    update_message = session.pop('update_message', '')

    task: Task = Task.query.get_or_404(id)
    
    if request.method == 'GET':
        return render_template('update.html', task=task, update_message=update_message)

    else:
        new_content = request.form.get('content', default='').strip()

        if new_content and new_content != task.content:
            try:
                task.content = new_content
                db.session.commit()
                update_message = 'Task updated successfully.'
                session['message'] = update_message
                return redirect(url_for('index'))
            except Exception as ex:
                update_message = f'Error updating task: {ex}'

        else:
            if not new_content:
                update_message = 'Task description must not be empty.'
            else:
                update_message = 'Task description must not be identical.'

    session['update_message'] = update_message
    return redirect(url_for('update', id=id))


if __name__ == '__main__':
    """Main entry point for the application."""
    app.run(debug=True)
