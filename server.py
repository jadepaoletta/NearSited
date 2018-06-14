from flask import (Flask, render_template, redirect, request, flash, session, jsonify)
from model import User, Friend, Trip, Attendee, Site, Favorite, Photo, Comment, connect_to_db, db
from helper import search_by_text, get_thumnail_url, send_trip_invite, cancel_trip, get_site_photos
from jinja2 import StrictUndefined
from flask_debugtoolbar import DebugToolbarExtension
import os
import bcrypt
import flickrapi
import datetime
import requests
import base64
import imghdr


app = Flask(__name__)

# import access keys and secrets
app.secret_key = "ABC"
FLICKR_API_KEY = os.environ['FLICKR_API_TOKEN']
FLICKR_API_SECRET = os.environ['FLICKR_API_SECRET']
GOOGLE_API_KEY = os.environ['GOOGLE_ACCESS_TOKEN_KEY']

# instantiate API objects
flickr = flickrapi.FlickrAPI(FLICKR_API_KEY, FLICKR_API_SECRET)


@app.route('/', methods=['GET', 'POST'])
def index():
    """Homepage"""

    return render_template("index.html")


@app.route('/login')
def login():
    """Returns a form for users to login"""

    # execute this if the user submitted the login form
    if request.args:
        email = request.args.get('email')
        password = request.args.get('password')


        if not User.query.filter_by(email=email).all():
            flash("I'm sorry, we couldn't find anyone with that email!")

        # execute if the user is found in the db
        else:
            current_user = User.query.filter_by(email=email).one()
            db_password = current_user.password.encode('utf-8')

            # execute this if the user's password is validated
            if bcrypt.hashpw(password.encode('utf-8'), db_password) == db_password:
                session['user_id'] = current_user.user_id
                return redirect('/')
            else:
                flash("Username and password do not match")

    return render_template("login.html")


@app.route('/register', methods=['GET'])
def register_form():
    """Returns a form for a new user to register."""
  
    return render_template("register.html")


@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    # if the user has submitted the register form, get the request vars
    fname = request.form['firstName']
    lname = request.form['lastName']
    phone = request.form['phoneNumber']
    email = request.form['email']
    password = request.form['password']

    #check if in db, else add to db
    if User.query.filter_by(email=email).all():
        flash("User already exists")

        return render_template("register.html")

    else:
        # hash the password because security is important
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # create and store the new user in the database
        new_user = User(fname=fname, lname=lname, email=email, password=hashed_pw, phone=phone)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.user_id

        return redirect("/")


@app.route('/sites')
def sites_list():
    """Return list of sites based on the location the user searched for."""

    user_location = request.args.get('search')
    places = search_by_text(user_location)

    final_places = []

    for place in places:
        site_in_db = Site.query.filter_by(site_id=place['place_id']).first()

        if site_in_db:
            final_places.append((place, site_in_db.thumbnail))

        elif 'photos' in place:
            # get photo via the photo reference
            thumb_url = get_thumnail_url(place['photos'][0]['photo_reference'])

            #store new site to db
            geo_location = place['geometry']['location']
            new_site = Site(site_id=place['place_id'], name=place['name'], address=place['formatted_address'], 
                        thumbnail=thumb_url, lat=geo_location['lat'], lng=geo_location['lng'])
            db.session.add(new_site)
            final_places.append((place, thumb_url))

    #commit the new places to the db
    db.session.commit()

    if not final_places:
        flash("Sorry, no results were found for your search! Please try again")

    return render_template("sites.html", places=final_places, api_key=GOOGLE_API_KEY)


@app.route('/sites/<site_id>')
def sites_details(site_id):
    """Returns a page displaying details about the specific site."""

    #get the place object from the DB
    place = Site.query.filter_by(site_id=site_id).one()

    flickr_photos = get_site_photos(place)

    friends = Friend.query.filter_by(user_id=session['user_id']).all()
    user_friends = []

    for friend in friends:
        current_friend = User.query.filter_by(user_id=friend.friend_id).first()
        user_friends.append(current_friend)

    uploaded_photos = Photo.query.filter_by(site_id=site_id).all()

    encoded_photos = [base64.b64encode(u_photo.photo_blob) for u_photo in uploaded_photos]

    comments = Comment.query.filter_by(site_id=site_id).all()

    user_comments = []
    for comment in comments:
        user_comments.append([base64.b64encode(comment.user.photo), comment])

    return render_template("site-details.html", place=place, photos=flickr_photos, 
        api_key=GOOGLE_API_KEY, friends=user_friends, u_photos=encoded_photos, comments=user_comments)
    

@app.route('/profile/<user_id>')
def user_profile(user_id):
    """Returns information about that specific user"""

    current_user = User.query.filter_by(user_id=user_id).first()

    return render_template('profile.html', user=current_user)
    

@app.route('/dashboard' )
def dashboard_view():
    """Returns the page to add a friend"""

    user_favorites = []
    user_trips = []
    user_friends = []
    user_photos = []

    if 'user_id' in session:
        favorites = Favorite.query.filter_by(user_id=session['user_id']).all()
        trips = Trip.query.filter_by(owner_id=session['user_id']).all()
        friends = Friend.query.filter_by(user_id=session['user_id']).all()
        user = User.query.filter_by(user_id=session['user_id']).first()
        photos = Photo.query.filter_by(user_id=session['user_id']).all()

        for favorite in favorites:
            fav_site = Site.query.filter_by(site_id=favorite.site_id).first()
            user_favorites.append(fav_site)

        for trip in trips:
            trip_site = Site.query.filter_by(site_id=trip.site_id).first()

            user_trips.append((trip, trip_site))

        for friend in friends:
            current_friend = User.query.filter_by(user_id=friend.friend_id).first()
            user_friends.append(current_friend)

        for photo in photos:
            encoded_photo = base64.b64encode(photo.photo_blob)
            user_photos.append([encoded_photo, photo])

        if user.photo:
            profile_photo = base64.b64encode(user.photo) 
            return render_template('dashboard.html', favorites=user_favorites, trips=user_trips, friends=user_friends, profile_photo=profile_photo, 
                                    user=user, photos=user_photos)


    return render_template('dashboard.html', favorites=user_favorites, trips=user_trips, friends=user_friends, user=user)


@app.route('/add-friend', methods=['POST'])
def add_friend_post():
    """Adds friend relationship to the database"""

    friend_email = request.form['friend']

    friend_user = User.query.filter_by(email=friend_email).first()

    friend_relationship = Friend(user_id=session['user_id'], friend_id=friend_user.user_id)
    friend_relationship2 = Friend(user_id=friend_user.user_id, friend_id=session['user_id'])

    db.session.add(friend_relationship)
    db.session.add(friend_relationship2)
    db.session.commit()

    return "Added {} as a friend".format(friend_user.fname)


@app.route('/logout')
def logout():
    """Logs out the user from the site"""

    del session['user_id']
    flash('Logged out')
    return redirect('/') 


@app.route('/favorite', methods=['POST'])
def favorite():

    site_id = request.form['path']

    favorite_in_db = Favorite.query.filter_by(user_id=session['user_id'], site_id=site_id).first()

    if favorite_in_db:
        return "Site is already in your favorites"

    else:
        favorite = Favorite(user_id=session['user_id'], site_id=site_id)
        db.session.add(favorite)
        db.session.commit()

        return "Saved to your favorites"


@app.route('/trip', methods=['POST'])
def trip():

    date = request.form['date'] 
    site_id = request.form['path']
    message = request.form['message']
    email_list = request.form.getlist('email_list[]')

    trip_date = datetime.datetime.strptime(date, "%m/%d/%Y")

    if trip_date.date() < datetime.datetime.today().date():
        return "Trip must be in the future"

    else:
        new_trip = Trip(site_id=site_id, owner_id=session['user_id'], date=date)
        db.session.add(new_trip)


    attendees = []
    if email_list:
        for email in email_list:
            attendee = User.query.filter_by(email=email).first()
            if attendee:
                attendees.append(attendee)
                send_trip_invite(new_trip, attendee, message)
                print "sent trip invite"
            else:
                print attendee + 'not found'

    db.session.commit()

    return "Successfully created a trip!"


@app.route('/cancel-trip', methods=['POST'])
def cancel_trip_view():

    trip_id = request.form['path']

    trip = Trip.query.filter_by(trip_id=trip_id).first()


    # check to see if there are trip attendees and delete them/send cancellation email
    if Attendee.query.filter_by(trip_id=trip_id).all():
        cancel_trip(trip)
        Attendee.query.filter_by(trip_id=trip_id).delete()

    Trip.query.filter_by(trip_id=trip_id).delete()
    db.session.commit()

    return "Canceled your trip"



@app.route('/trip-details/<trip_id>')
def trip_details(trip_id):

    trip = Trip.query.filter_by(trip_id=trip_id).first()

    return render_template('trip-details.html', trip=trip, api_key=GOOGLE_API_KEY)


@app.route('/confirm-trip/<trip_id>/<user_id>')
def confirm_trip(trip_id, user_id):
    
    new_attendee = Attendee(trip_id=int(trip_id), attendee_id=int(user_id))
    db.session.add(new_attendee)
    db.session.commit()

    flash('Thanks for confirming!' )
    return redirect('/')


@app.route('/upload-photo', methods=['POST'])
def upload_photo():

    file = request.files['image']
    site_id = request.form['site_id']

    new_photo = Photo(photo_blob=file.read(), user_id=session['user_id'], site_id=site_id, date=datetime.datetime.today().date())

    db.session.add(new_photo)
    db.session.commit()

    return redirect('/sites/{}'.format(site_id))


@app.route('/upload-profile-photo', methods=['POST'])
def upload_profile_photo():

    file = request.files['image']
    profile_photo = file.read()

    supported_types = ['jpeg', 'png']
    file_type = imghdr.what(None, profile_photo)

    print file_type

    if file_type in supported_types:

        user = User.query.filter_by(user_id=session['user_id']).first()
        user.photo = profile_photo
        db.session.commit()

    else:
        print "invalid type"

    return redirect('/dashboard')


@app.route('/post-comment', methods=['POST'])
def post_comment():

    comment = request.form['comment']
    site_id = request.form['site_id']

    print comment

    new_comment = Comment(comment_string=comment, user_id=session['user_id'], site_id=site_id, date=datetime.datetime.today().date())

    db.session.add(new_comment)
    db.session.commit()

    #get the user's profile photo and base64 encode it
    #send the comment and photo in a JSON

    return "Thanks for your comment"



if __name__ == "__main__":
    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)


    DebugToolbarExtension(app)
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.run(port=9810, host='0.0.0.0')

