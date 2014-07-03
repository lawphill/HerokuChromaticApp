from flask import render_template, request
from app import app
from chromatic import process_data, default_page

@app.route('/',methods=['POST','GET'])
@app.route('/index',methods=['POST','GET'])
def index():
    if request.method == 'POST':
        c = process_data(request)
    else:
        c = default_page(request)

    return render_template("chromatic.html",
        c = c)

@app.route('/login',methods=['POST','GET'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        error = None
    else:
        error = 'Wrong password'

    return render_template('form.html',
        form = form,
        error = error)
    
        
