from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_from_directory
from werkzeug import secure_filename
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from catalog_db import Base, Category, Item, User
import os

# imports for login session
from flask import session as login_session
import random
import string

# imports for goole plus authentication
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

from functools import wraps

app = Flask(__name__)

# upload files only following extensions
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
# upload folder path
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
# the maximum allowed payload to 16 megabytes
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# for goole plus authentication
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# login page
@app.route('/login')
def show_login():
    # Create anti-forgery state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state, user=logged_in())

# logout page
@app.route('/logout')
def show_logout():
    return render_template('logout.html', user=logged_in())

# CONNECT - Get a current user's token and set their login_session
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists. if it doesn't, make a new one.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    flash("you are now logged in as %s" % login_session['username'])
    output = { 'username': login_session['username'], 'picture': login_session['picture'] }
    return jsonify(output)

# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = json.loads(login_session.get('credentials'))
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # Reset the user's sesson.
    del login_session['credentials']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']

    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user. But disconnected anyway.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

def logged_in():
    if 'user_id' not in login_session:
        return { 'id': '' }
    else:
        return { 'id': login_session['user_id'], 'name': login_session['username'],
                 'photo': login_session['picture'] }


# Category Helper Functions
def get_all_categories():
    return session.query(Category).order_by(asc(Category.name)).all()

# Image upload related Functions
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def upload_file(file, id):
    if file and allowed_file(file.filename):
        filename = str(id) + '_' + secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    return ""

def delete_file(filename):
    if filename:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return ""
# Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in login_session:
            return redirect(url_for('show_login'))
        return f(*args, **kwargs)
    return decorated_function

# JSON APIs to view Catalog Information
@app.route('/item/JSON')
def catalogJSON():
    items = session.query(Item).join(Category).order_by(Item.category_id, Item.id).all()
    return jsonify(Items=[i.serialize for i in items])

@app.route('/category/<int:category_id>/item/JSON')
def itemsByCategoryJSON(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(Item).filter_by(category_id = category_id).order_by(desc(Item.name)).all()
    return jsonify(Items=[i.serialize for i in items])

@app.route('/item/<int:item_id>/JSON')
def itemJSON():
    item = session.query(Item).join(Category).one()
    return jsonify(Item=item.serialize)

# image uploading
@app.route('/static/uploads/<path:path>')
def send_uploaded_image(path):
    return send_from_directory(app.config['UPLOAD_FOLDER'], path)

# root page and display 10 recent added items.
@app.route('/')
def show_home():
    # select 10 latest items with category name for each item
    items = session.query(Item).join(Category).order_by(desc(Item.id)).limit(10)
    return render_template('home.html', categories = get_all_categories(),
        items = items, user=logged_in())

# item list page by a category
@app.route('/category/<int:category_id>')
@app.route('/category/<int:category_id>/item')
def show_items_by_category(category_id):
    # get the category information for the page and then get all items in the category
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(Item).filter_by(category_id = category_id).order_by(desc(Item.name)).all()
    return render_template('itemlist.html', categories = get_all_categories(),
        items = items, category = category, user=logged_in())

# create item
@app.route('/item/new', methods=['GET', 'POST'])
@login_required
def new_item():
    if request.method == 'POST':
        newItem = Item( name = request.form['name'],
            description = request.form['description'],
            category_id = request.form['category_id'],
            user_id = login_session['user_id'])
        session.add(newItem)
        session.commit()
        # image file upload with new prefix
        filename = upload_file(request.files['file'], newItem.id)
        if filename:
            newItem.image_path = filename
            # modify image path as new filename
            session.add(newItem)
            session.commit()

        flash('New Item %s Successfully Created' % newItem.name)
        return redirect(url_for('show_items_by_category', category_id=newItem.category_id))
    else:
        return render_template('new_item.html', categories = get_all_categories(), user=logged_in())

# display a item
@app.route('/item/<int:item_id>')
def show_item(item_id):
    # get the category information for the page and then get all items in the category
    try:
        item = session.query(Item).filter_by(id = item_id).one()
    except NoResultFound, e:
        return redirect(url_for('show_home'))
    category = session.query(Category).filter_by(id = item.category_id).one()
    return render_template('item.html', categories = get_all_categories(),
        item = item, category = category, user=logged_in())

# modify item
@app.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    editedItem = session.query(Item).filter_by(id = item_id).one()
    category = session.query(Category).filter_by(id = editedItem.category_id).one()
    if request.method == 'POST':
        # remove old image file
        delete_file(editedItem.image_path)
        # and upload new image file
        filename = upload_file(request.files['file'], editedItem.id)
        editedItem.image_path = filename
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category_id']:
            editedItem.category_id = request.form['category_id']
        session.add(editedItem)
        session.commit()
        flash('Item %s Successfully Updated' % editedItem.name)
        return redirect(url_for('show_item', category_id=editedItem.category_id, item_id=item_id))
    else:
        return render_template('edit_item.html',
            categories = get_all_categories(), item = editedItem, category = category)

# delete item
@app.route('/item/<int:item_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    itemToDelete = session.query(Item).filter_by(id = item_id).one()
    category = session.query(Category).filter_by(id = itemToDelete.category_id).one()
    if request.method == 'POST':
        # remove mage file
        delete_file(itemToDelete.image_path)
        session.delete(itemToDelete)
        session.commit()
        flash('Item %s Successfully Deleted' % itemToDelete.name)
        return redirect(url_for('show_items_by_category', category_id=itemToDelete.category_id))
    else:
        return render_template('delete_item.html', item = itemToDelete, category = category,  user=logged_in())

# create new category
@app.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    if request.method == 'POST':
        newCategory = Category( name = request.form['name'],
            user_id = login_session['user_id'])
        session.add(newCategory)
        session.commit()

        flash('New Category %s Successfully Created' % newCategory.name)
        return redirect(url_for('show_home'))
    else:
        return render_template('new_category.html', user=logged_in())

# modify the category
@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    editedCategory = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        session.add(editedCategory)
        session.commit()
        flash('Category %s Successfully Updated' % editedCategory.name)
        return redirect(url_for('show_home'))
    else:
        return render_template('edit_category.html', category = editedCategory)

# delete category
@app.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_category(category_id):
    categoryToDelete = session.query(Category).filter_by(id = category_id).one()
    item_count = session.query(Item).filter_by(category_id = categoryToDelete.id).count()
    if request.method == 'POST':
        if item_count < 1:
            session.delete(categoryToDelete)
            session.commit()
            flash('Item %s Successfully Deleted' % categoryToDelete.name)
            return redirect(url_for('show_home'))
    else:
        return render_template('delete_category.html', category = categoryToDelete, numberOfItems= item_count)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
