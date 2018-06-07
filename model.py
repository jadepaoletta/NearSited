"""Models and database functions for NearSited"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

##############################################################################
# Model definitions

class User(db.Model):
    """User of NearSited website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    fname = db.Column(db.String(25), nullable=False)
    lname = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    photo = db.Column(db.LargeBinary, nullable=True)

    # Define relationship to trip
    trip = db.relationship("Trip",
                            backref=db.backref("users",
                                               order_by=user_id))

    # Define relationship to favorite
    favorite = db.relationship("Favorite",
                                backref=db.backref("users", 
                                                    order_by=user_id))

    # Define relationship to attendee
    attendee = db.relationship("Attendee",
                                backref=db.backref("users",
                                                    order_by=user_id))

    def __repr__(self):
        """Returns the id and name of the User object"""

        return "< id: {} name: {} {} >".format(self.user_id, self.fname, self.lname)


class Friend(db.Model):
    """Friend relationship in NearSited website."""

    __tablename__ = "friends"

    relationship_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    # Define relationship to primary user friend
    primary_friend = db.relationship("User", foreign_keys=[user_id])
    
    # Define relationship to secondary user friend
    secondary_friend = db.relationship("User", foreign_keys=[friend_id])

    def __repr__(self):
        """Returns the id and name of the User object"""

        return "< user: {} friend: {} >".format(self.user_id, self.friend_id)


class Trip(db.Model):
    """Trip planned by a user in the NearSited website."""

    __tablename__ = "trips"

    trip_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    site_id = db.Column(db.String(100), db.ForeignKey('sites.site_id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    # Define relationship to attendee
    trip_attendees = db.relationship("Attendee",
                                backref=db.backref("trips",
                                                    order_by=trip_id))

    # Define relationship to site
    site = db.relationship("Site",
                                backref=db.backref("trips",
                                                    order_by=trip_id))

    def __repr__(self):
        """Returns details of the Trip object"""

        return "< trip to site: {} at: {} by user {}>".format(self.site_id, self.date, self.owner_id)


class Attendee(db.Model):
    """Attendee for a trip in the NearSited website."""

    __tablename__ = "trip_attendees"

    ta_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.trip_id'), nullable=False)
    attendee_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    def __repr__(self):
        """Returns details of the Attendee object"""

        return "< trip: {} attendee_id {}>".format(self.trip_id, self.attendee_id)


class Site(db.Model):
    """Site in the NearSited website."""

    __tablename__ = "sites"

    site_id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    thumbnail = db.Column(db.String(200), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)

    # Define relationship to favorite_sites
    favorite = db.relationship("Favorite",
                                backref=db.backref("sites",
                                                    order_by=site_id))
    def __repr__(self):
        """Returns details of the Site object"""

        return "< id: {} name: {}>".format(self.site_id, self.name)


class Favorite(db.Model):
    """A User's favorite site in the NearSited website."""

    __tablename__ = "favorite_sites"

    fs_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    site_id = db.Column(db.String(100), db.ForeignKey('sites.site_id'), nullable=False)

    def __repr__(self):
        """Returns details of the Site object"""

        return "< user: {} site: {}>".format(self.user_id, self.site_id)


class Photo(db.Model):
    """Photo in NearSited website."""

    __tablename__ = "photos"

    photo_id = db.Column(db.Integer, primary_key=True)
    photo_blob = db.Column(db.LargeBinary, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    site_id = db.Column(db.String(100), db.ForeignKey('sites.site_id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    user = db.relationship("User", 
                            backref=db.backref("photos", order_by=photo_id))

    site = db.relationship("Site", 
                            backref=db.backref("photos", order_by=photo_id))

    def __repr__(self):
        """Returns details of photo."""

        return "< photo added by user: {} on site: {}>".format(self.user_id, self.site_id)


class Comment(db.Model):
    """Comment on a site in NearSited website."""

    __tablename__ = "comments"

    comment_id = db.Column(db.Integer, primary_key=True)
    comment_string = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    site_id = db.Column(db.String(100), db.ForeignKey('sites.site_id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    user = db.relationship("User", 
                            backref=db.backref("comments", order_by=comment_id))

    site = db.relationship("Site", 
                            backref=db.backref("comments", order_by=comment_id))





##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///nearsited'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."

























