# Task Master Web App

My version of the Flask web app from the great [freeCodeCamp.org](https://freeCodeCamp.org) tutorial at [https://www.youtube.com/watch?v=Z1RJmh_OqeA].

Live app: [https://taskmastertut.herokuapp.com]

## Development Requirements

### Mandatory

You need a `.env` file in the project root containing at least your secret key (`SESSION_KEY`) for session variables, eg.:

    SESSION_KEY=foobarbaz

On `Heroku` you need to manually add the variable under your application's "`Settings`" - "`Config Vars`" section.

### Optional

A `.flaskenv` file in the project root simplifies testing using `flask run` a lot. Example contents:

    FLASK_APP=app.py
    FLASK_ENV=development

## Linting Kudos

Linting (or "IntelliSense" as some might call it) for entity models based on `Flask SQLAlchemy` is currently totally broken in `VS Code`, for both `Pylance` and `Jedi`.

Gladly, a very smart person (Kudos: **WilsonPhooYK**) came up with a feasible workaround - requiring to add some esoterical stub code to a project, but not too bad:

* [https://github.com/microsoft/pylance-release/issues/187]
* [https://github.com/WilsonPhooYK/udemy-automated-software-testing-python/blob/main/section6_7/typings/]

The most essential "odd" lines deviating from standard `Flask SQLAlchemy` boil down to:

    # This at the top of the code file will help with pylint:
    # pylint: disable=too-few-public-methods

    from typing import cast
    
    # Regular Flask imports here

    # typings stuff is from GitHub repository linked above
    from typings.sql_alchemy import SQLAlchemy as SQLAlchemyStub
    
    db = cast(SQLAlchemyStub, SQLAlchemy(app))
    Model = db.Model

    # Entity class needs to inherit from type alias
    class Entity(Model):
        __tablename__ = ...
        foo = db.Column(...)
        ...
