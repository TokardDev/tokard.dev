import sqlite3

import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def get_url_from_code(code):
    db = get_db()
    url = db.execute(
        'SELECT link FROM redirects WHERE code = ?', (code,)
    ).fetchone()
    if url != None:
        return url[0]
    else:
        return "/"

def insert_url(link, code):
    # si le link ne commence pas par "https:// ou http://" on ajoute http://
    if not link.startswith("http://") and not link.startswith("https://"):
        link = "http://" + link
    db = get_db()
    existing_entry = db.execute(
        'SELECT code FROM redirects WHERE code = ?', (code,)
    ).fetchone()

    if existing_entry:
        return None
    db.execute(
        'INSERT INTO redirects (link, code) VALUES (?, ?)',
        (link, code)
    )
    db.commit()
    return code

