"""Application entry point."""
import flask_login
from flask import Flask, render_template, request, url_for, flash, session
from forms import registration, login
from DB_API import *
from flask_login import LoginManager, login_required, current_user, login_user, logout_user

app = Flask(__name__)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.config['SECRET_KEY'] = '_5#y2LF4Q8z*n*xec]/'

@login_manager.user_loader
def load_user(user_id):
    user = load_user_helper(user_id)
    return user

@app.route('/')
def hello_moto():
    return render_template("HomePage.html")

@app.route('/home')
def home():
    return render_template("HomePage.html")

@app.route('/login', methods=['GET', 'POST'])
def log_in():
    #check for POST submition of form
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_object = login(username, password)
        print(user_object)
        if user_object != None:
            login_user(user_object)
            space = get_space(user_object.rootSpace)
            return render_template('design.html', subspaces = space.spaces, items = space.items, space_name = space.name, space_id = space.id)
        else:
            flash('Invalid Credentials please try again.') #this and the line above need to be tested one might work hopefully
            return render_template("login.html")
    return render_template("login.html")

@app.route('/createAccount', methods=['GET','POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        action = registration(username, email,  password)
        #check here to see if the email and username has already been used by performing a query
        #if the above query is true flash the below message and direct back to the signup page using:
        #return redirect(url_for('app.createAccount'))
        #flash('Email address already exists')
        #create a new user with the form data and hash the password so the plaintext version isn't saved this is where we canc all the method in forms.py
        #add the new user to the database
        if action == 409:
            flash('Username already exists')
            return render_template('register.html')
        elif action == 410:
            flash('Email address already exists')
            return render_template("register.html")
        else:
            flash('Thank you for creating your account '+username)
            return render_template("login.html")
    return render_template("register.html")

@app.route('/design', methods=['GET','POST'])
@login_required
def space_design():

    try:
        urlRequest = request.url
        urlRequest = urlRequest.split('?')
        urlRequest = urlRequest[1]
        urlRequest = urlRequest.split('=')
        space_id = urlRequest[1]

        print(space_id)
        space = get_space(space_id)
        return render_template("design.html", subspaces = space.spaces, items = space.items, space_name = space.name, space_id = space.id, parent_space = space.parent_space)
        print(urlRequest)
    except:
        pass

    if '_user_id' in session.keys():
        user = load_user(session['_user_id'])
        space = get_space(user.rootSpace)

    if request.method == 'POST':
        form = request.form['formSelector']

        if 'addspace' in request.form:
            spaceName = request.form['spaceName']
            parentSpaceName = request.form['parentSpaceName']

            action = addSpace(spaceName, parentSpaceName)
            space = get_space(parentSpaceName)
            if action == 409:
                flash('Space name already exists')
                return render_template("design.html", subspaces = space.spaces, items = space.items, space_name = space.name, space_id = space.id, parent_space = space.parent_space)
            elif action == 410:
                flash('Parent space does not exist')
                return render_template("design.html", subspaces = space.spaces, items = space.items, space_name = space.name, space_id = space.id, parent_space = space.parent_space)
            else:
                return render_template("design.html", subspaces = space.spaces, items = space.items, space_name = space.name, space_id = space.id, parent_space = space.parent_space)
        elif 'deleteform' in request.form:
            # parentSpaceName = request.form['parentSpaceName']
            # space = get_space(parentSpaceName)
            itemChoice = request.form['choice1']
            subspaceChoice = request.form['choice2']
            print(itemChoice)
            print(subspaceChoice)

            deleteSpace(subspaceChoice)
            deleteItem(itemChoice)

            user = load_user(session['_user_id'])
            space = get_space(user.rootSpace)

            return render_template("design.html", subspaces=space.spaces, items=space.items, space_name=space.name, space_id=space.id, parent_space=space.parent_space)
        elif 'addItem' in request.form:
            itemName = request.form['itemName']
            parentSpaceID = request.form['parentSpaceID']

            action = quickAddItem(itemName, parentSpaceID)
            space = get_space(parentSpaceID)
            print(action)
            if action == 410:
                flash('This item already exists.')
                return render_template("design.html", subspaces=space.spaces, items=space.items, space_name=space.name,
                                       space_id=space.id, parent_space=space.parent_space)
            else:
                return render_template("design.html", subspaces=space.spaces, items=space.items, space_name=space.name,
                                       space_id=space.id, parent_space=space.parent_space)
        else:
            pass



    """
    #test data to test the front end functionality
    subspaces_dict = {"Living Room" : "home",
                      "Kitchen" : "login",
                      "Dining Room" : "createAccount"}
    items_dict = {"Coasters" : "2343",
                  "Fabreeze" : "23234",
                  "Paper Towel" : "2212",
                  "Lip Balm" : "9985"}
    spaceName = "Bobert's Space"
    """

    return render_template("design.html", subspaces = space.spaces, items = space.items, space_name = space.name, space_id = space.id, parent_space=space.parent_space)

@app.route('/details')
@login_required
def detail_page():
    return render_template("itemdetails.html")

@app.route('/load')
@login_required
def loading_page():
    return render_template("loaditems.html")

@app.route('/find')
@login_required
def query_page():
    return "This is the query page."

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template("HomePage.html")

@app.errorhandler(500)
def pageNotFound(error):
    flash('Please login or create an account first')
    return render_template("login.html")



"""Things to do.
Add back end for design page. -- Trevor

Interface with the buttons for add space, and delete. -- Reid

Customize login required to not throw internal server error. --Trevor

Finish loading page tasks. 

For nav bar if you click on user icon it has drop down that has options for logout if the current_user.is_authenticated == True or login/registration if current_user.is_authenticated == False

Hydrate
"""

