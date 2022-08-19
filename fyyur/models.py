# from datetime import datetime
import dateutil.parser

from flask import flash

from fyyur import db

class Venue(db.Model):
    __tablename__ = "venues"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500), default="https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60")
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    shows = db.relationship(
            "Show", backref = "venue", cascade = "all, delete-orphan", lazy = True
            )
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(120))

    # Completed: implement any missing fields, as a database migration using Flask-Migrate

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.update(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<Venue {self.name}>"


class Artist(db.Model):
    __tablename__ = "artists"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500), default="https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80")
    facebook_link = db.Column(db.String(120))
    shows = db.relationship(
            "Show", backref = "artist", cascade = "all, delete-orphan", lazy = True
            )
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(120))

    # Done: implement any missing fields, as a database migration using Flask-Migrate

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.update(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<Artist {self.name}>"


class Show(db.Model):
    __tablename__ = "shows"
    id = db.Column(db.Integer, primary_key = True)
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), nullable = False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"), nullable = False)
    start_time = db.Column(db.DateTime, nullable = False)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.update(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<Show of artist with id: {self.artist_id} and venue with id: {self.venue_id}>"


# Completed Implement Show and Artist models, and complete all model relationships and properties,
# as a database migration.