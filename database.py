from flask import g

import sqlite3

def connect_to_database():
    sql=sqlite3.connect('C:/Users/summer/Desktop/todays_project/projapp.db')
    sql.row_factory = sqlite3.Row
    return sql

def get_database():
    if not hasattr(g, 'projapp_db'):
        g.projapp_db = connect_to_database()

    return g.projapp_db