from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
import re
emailRegEx = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
passwordCharUppercaseRegEx = re.compile(r'[A-Z]+')
passwordNumRegEx = re.compile(r'[0-9]+')

app = Flask(__name__)
mysql = MySQLConnector(app,'friendsdb')
app.secret_key = 'KeepItSecretKeepItSafe'

@app.route('/users')
def index():
  query = 'SELECT * FROM friends'
  friends = mysql.query_db(query)
  return render_template("/users.html", friend_list=friends)

@app.route('/users/new')
def addUserPage():
  return render_template("/new.html")

@app.route('/users/new', methods=['POST'])
def addUser():
    query = "SELECT * FROM friends"
    friends_query = mysql.query_db(query)

    errorFlag = False
    session['firstName'] = request.form['firstName']
    session['lastName'] = request.form['lastName']
    session['email'] = request.form['email']

    if len(session['firstName']) < 2:
      flash("first name cannot be empty!", 'error')
      errorFlag = True
    elif session['firstName'].isalpha() == False :
      flash("First name must contain only alphabetic characters!", 'error')
      errorFlag = True
    
    if len(session['lastName']) < 2:
      flash("Last name cannot be empty!", 'error')
      errorFlag = True
    elif session['lastName'].isalpha() == False :
      flash("Last name must contain only alphabetic characters!", 'error')
      errorFlag = True

    if len(session['email']) < 1:
      flash("email cannot be empty!", 'error')
      errorFlag = True
    elif not emailRegEx.match(session['email']):
      flash("Invalid Email Address!")
      errorFlag = True   

    for x  in friends_query:
        if x['email'] == request.form['email'] :
            flash("Error! Duplicate email", 'incorrect')
            errorFlag = True
            return render_template('users.html')
    if errorFlag == True :
      return redirect('/users')      

    create_user(request)
    return render_template('/users.html')
    
def create_user(request):
  query = "INSERT INTO friends (email, first_name, last_name, created_at, updated_at) VALUES (:email, :first_name, :last_name, NOW(), NOW())"
  data = {
             'email'  : request.form['email'],
             'first_name'     : request.form['firstName'],
             'last_name'      : request.form['lastName'],
            }
  
  new_user = mysql.query_db(query, data)
  session['user'] = new_user
  return True

@app.route('/friends/<id>/edit')
def edit(id):
    query = "SELECT * FROM friends WHERE id = :friend_id LIMIT 1"
    data = {
        "friend_id": id
    }
    friend = mysql.query_db(query, data)
    return render_template("/edit.html", user=friend)

@app.route('/users/<id>', methods=['POST'])
def update(friend_id):
    query = "UPDATE friends SET first_name = :first_name, last_name = :last_name, updated_at=NOW() WHERE id = :id LIMIT 1"
    data = {
             'first_name': request.form['first_name'],
             'last_name':  request.form['last_name'],
             'email': request.form['email'],
             'id': id
           }
    mysql.query_db(query, data)
    return render_template('/edit.html', )
@app.route('/users/<id>/delete', methods=['POST'])
def destroy(id):
  query = 'DELETE FROM friends WHERE id = :friend_id'
  data = {
          'friend_id': id
    }
  mysql.query_db(query, data)
  return redirect('/users')

app.run(debug=True) # run our servers