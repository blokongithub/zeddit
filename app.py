import flask
from flask import Flask, request, jsonify, render_template, redirect, make_response, send_file
import backend

app = flask.Flask(__name__)
HOST = 5000

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in request.cookies:
        return redirect('/home')
    
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        if 'loginsubmit' in request.form:
            
            if(request.form['name'] != '' and request.form['password'] != '' and request.form['loginsubmit'] != ''):
                if backend.login(request.form['name'], request.form['password']) == True:
                    resp = make_response(redirect('/home'))
                    resp.set_cookie('username', request.form['name'])
                    return resp
                else:
                    return "<html><body><h1>Error 3, password incorrect, please try again </h1></body></html>"
            
        elif(request.form['name'] != '' and request.form['password'] != '' and request.form['new'] != ''):
            
            if len(request.form['password']) < 8 or len(request.form['password']) > 20 or len(request.form['name']) > 20:
                return "<html><body><h1>Error 4, password too long or short, please try again, you need 8 characters </h1></body></html>"
            backend.createuser(request.form['name'], request.form['password'])
            resp = make_response(redirect('/home'))
            resp.set_cookie('username', request.form['name'])
            return resp
        else:
            return "<html><body><h1>Error, username or password is empty, please try again </h1></body></html>"
        
@app.route("/logout")
def logout():
    resp = make_response(redirect('/login'))
    resp.set_cookie('username', '', expires=0)
    return resp

@app.route("/z/<subzeddit>")
def subzeddit(subzeddit):
    if 'username' not in request.cookies:
        return redirect('/login')
    resp = make_response(render_template('subzeddit.html', subzed = backend.getsubzeddit(subzeddit), posts = backend.getposts(subzeddit))) #TODO
    return resp

@app.route("/z/<subzeddit>/post", methods=["GET", "POST"])
def post(subzeddit):
    if 'username' not in request.cookies:
        return redirect('/login')
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        if title and content:
            print("Creating post", title, content)
            backend.createpost(subzeddit, request.cookies['username'], title, content)
            return redirect(f'/z/{subzeddit}')
    if request.method == 'GET':
        return render_template('makepost.html', subzeddit = subzeddit)
    
@app.route("/u/<uuid>")
def user(uuid):
    if 'username' not in request.cookies:
        return redirect('/login')
    resp = render_template('userprofile.html', user = backend.getuserinfo(uuid), posts = backend.getuserposts(uuid)) #TODO
    return resp

@app.route("/profile")
def userprofile():
    if 'username' not in request.cookies:
        return redirect('/login')
    usrname = request.cookies['username']
    uuid = backend.getuserid(usrname)
    resp = render_template('userprofile.html', user = backend.getuserinfo(uuid), posts = backend.getuserposts(uuid)) #TODO
    return resp

@app.route("/")
def index():
    if 'username' in request.cookies:
        resp = make_response(redirect('/login'))
        return resp
    resp = make_response(redirect('/home'))
    return resp

@app.route("/home")
def home():
    if 'username' not in request.cookies:
        return redirect('/login')
    posts = backend.getposts("admin")
    return render_template('home.html', posts = posts)       

@app.route("/search/", methods=['GET', 'POST'])
def search():
    if 'username' not in request.cookies:
        return redirect('/login')
    
    if request.method == 'POST':
        query = request.form.get('query')
        return "not used yet"
    
    query = request.args.get('query')
    if not query:
        return make_response("Error 5, please use the search bar to search for a subzeddit or user")
    
    #results = backend.search(query) TODO
    response = backend.search(query)
    resp = make_response(str(response)) #TODO
    return resp

@app.route("/createsubzeddit", methods=['GET', 'POST'])
def makezeddit():
    if 'username' not in request.cookies:
        return redirect('/login')
    if request.method == 'GET':
        resp = make_response(render_template('createsubzeddit.html')) # TODO
        return resp
    if request.method == 'POST':
        if(request.form['link'] != '' and request.form["title"] != "" and request.form['description'] != ''):
            backend.createsubzeddit(request.form['link'], request.cookies["username"], request.form["title"],  request.form['description'])
            resp = make_response(redirect(f'/z/{request.form["link"]}'))
            return resp
        else:
            resp = make_response("<html><body><h1>Error 6, please fill out all fields</h1></body></html>")
            return resp
    

@app.errorhandler(404)
def page_not_found(e):
    return render_template('placeholder.html'), 404 #TODO

if __name__ == '__main__':
    backend.initialize()
    print(f"✅ Flask server running at http://127.0.0.1:{HOST} ✅")
    app.run(debug=True, port=HOST)

