from flask import Flask, url_for, request, redirect, session, g, flash, get_flashed_messages
from flask.templating import render_template
from database import get_database
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = 'summer'



@app.route('/')
def index():
    return render_template('home.html')

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

@app.route('/login', methods=["POST", "GET"])
def login():
    error = None
    db = get_database()
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        user_curs = db.execute('select * from users where name = ?', [name])
        user = user_curs.fetchone()

        if user:
            if check_password_hash(user['password'], password):
                session['logged_in'] = True
                return redirect(url_for('dashboard'))
            
            else:
                error = "Username or Password did not match"
        else:
            error = "Username or Password did not match, Try again"
    return render_template('login.html', loginerror = error)

@app.route('/register', methods=["POST", "GET"])
def register():
    db = get_database()
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        dbuser_cursr = db.execute('select * from users where name = ?', [name])
        existing_username = dbuser_cursr.fetchone()
        if existing_username:
            return render_template('register.html', registererror = 'Username has already been taken, try again')
        db.execute('insert into users (name, password) values (?, ?)', [name, hashed_password])
        db.commit()
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_database()
    emp_cur = db.execute('select * from emp')
    all_emp = emp_cur.fetchall()
    return render_template('dashboard.html', all_emp = all_emp)

@app.route('/addnewemployee', methods=["POST", "GET"])
def addnewemployee():
    db = get_database()
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        db.execute('insert into emp (name, email, phone, address) values(?,?,?,?)',[name, email, phone, address])
        db.commit()
        return redirect(url_for('dashboard'))
    return render_template('addnewemployee.html')

@app.route('/singleemp/<int:empid>')
def singleemp(empid):

    db = get_database()
    emp_curs = db.execute('select * from emp where empid = ?', [empid])
    single_emp = emp_curs.fetchone()
    return render_template('singleemp.html', single_emp = single_emp)

@app.route('/fetchone/<int:empid>')
def fetchone(empid):
    db = get_database()
    emp_curs = db.execute('select * from emp where empid = ?', [empid])
    single_emp = emp_curs.fetchone()
    return render_template('updateemployee.html', single_emp = single_emp)

@app.route('/updateemployee', methods=["GET", "POST"])
def updateemployee():
    if request.method == 'POST':
        empid = request.form['empid']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        db = get_database()
        db.execute('update emp set name = ?, email = ?, phone = ?, address = ? where empid = ?', [name, email, phone, address, empid])
        db.commit()
        return redirect(url_for('dashboard'))

    return render_template('updateemployee.html')

@app.route('/deleteemp/<int:empid>', methods = ["POST", "GET"])
def deleteemp(empid):
    db = get_database()
    if request.method == "GET":
        db.execute('delete from emp where empid = ?', [empid])
        db.commit()
        return redirect(url_for('dashboard'))
    return render_template('dashboard.html')



@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug = True)