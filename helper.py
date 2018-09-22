from model import User, Friend, Trip, Attendee, Site, Favorite, Photo, Comment, connect_to_db, db
import requests
import flickrapi
import os

################################################################################
# THESE ARE MY HELPER FUNCTIONS
################################################################################


FLICKR_API_KEY = os.environ['FLICKR_API_TOKEN']
FLICKR_API_SECRET = os.environ['FLICKR_API_SECRET']
GOOGLE_API_KEY = os.environ['GOOGLE_ACCESS_TOKEN_KEY']
MAILGUN_API_KEY = os.environ['MAILGUN_API_KEY']

# instantiate API objects
flickr = flickrapi.FlickrAPI(FLICKR_API_KEY, FLICKR_API_SECRET)


def search_by_text(location):
    """Takes in a user location and returns a list of relevant place objects."""

    search_params = {'query': 'scenic places near '+ location, 
                    'key': GOOGLE_API_KEY}

    query_result = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json', params=search_params)

    places_dict = query_result.json() #get back a dictionary

    do_not_want = set(["shopping_mall", "lodging", "restaurant", "food"])
    places = places_dict['results']
    
    final_places = []

    for place in places:
        if not (set(place['types']) & do_not_want): # if any of the types are in the do not want list
            final_places.append(place)

    #returns a list of place objects
    return final_places 


def get_thumnail_url(photo_reference):
    """Takes in a photo reference and returns the url of the thumbnail."""

    thumb_params = {'key': GOOGLE_API_KEY, 
                    'photoreference': photo_reference, 
                    'maxheight': 200}

    thumbnail = requests.get('https://maps.googleapis.com/maps/api/place/photo?parameters', params=thumb_params)

    return thumbnail.url


def get_site_photos(place):
    """Takes in the site ID and returns a list of large photos from flickr"""

    photos = flickr.photos.search(lat=place.lat,lon=place.lng, text=place.name,
                                    sort='interestingness-desc', extras='url_l', format='etree')

    # Gets all of the photo elements in the response
    flickr_photos = photos.find('photos').findall('photo')

    # Loop through photos to only get the large ones
    large_photos = [photo for photo in flickr_photos if 'url_l' in photo.attrib]

    return large_photos



def send_trip_invite(trip, trip_attendee, message=None):

    attendee_email = trip_attendee.email
    attendee_name = trip_attendee.fname
    attendee_id = trip_attendee.user_id
    site_name = trip.site.name
    owner_email = trip.users.email
    owner_name = trip.users.fname

    return requests.post(
        "https://api.mailgun.net/v3/sandbox326257be797843b5b21fc9e469cd7edb.mailgun.org/messages",
        auth=("api", MAILGUN_API_KEY),
        data={"from": "NearSited <postmaster@sandbox326257be797843b5b21fc9e469cd7edb.mailgun.org>",
              "to": "{} <{}>".format(attendee_name, attendee_email), 
              "subject": "You have been invited by {} to go on a trip!".format(owner_name),
              "text": '''Hello there, {} would like to invite you on a trip to {}. 
              Message from {}: "{}"'''.format(owner_name, site_name, owner_name, message)})



def cancel_trip(trip):

    attendee_email = trip.trip_attendees[0].users.email
    attendee_name = trip.trip_attendees[0].users.fname
    site_name = trip.site.name
    owner_email = trip.users.email
    owner_name = trip.users.fname

    return requests.post(
        "https://api.mailgun.net/v3/sandbox326257be797843b5b21fc9e469cd7edb.mailgun.org/messages",
        auth=("api", MAILGUN_API_KEY),
        data={"from": "NearSited <postmaster@sandbox326257be797843b5b21fc9e469cd7edb.mailgun.org>",
              "to": "{} <{}>".format(attendee_name, attendee_email), 
              "subject": "Your trip has been cancelled",
              "text": 'Hello there, your trip with {} to {} has been cancelled!'.format(owner_name, site_name)})
