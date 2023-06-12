from flask_sqlalchemy import SQLAlchemy
# from app import app
# # from flask import Flask, render_template, request, Response, flash, redirect, url_for ,jsonify, abort

db = SQLAlchemy()

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False,unique=True)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False,unique=True)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120),nullable=True)
    genres = db.Column(db.ARRAY(db.String(120)),nullable=False)
    website_link = db.Column(db.String(120),nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120),nullable=True)
    Show = db.relationship('Show', backref ='venue',lazy = True)

    def __repr__(self):
        return f'<venue {self.id} {self.name}>'
    
class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False,unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False,unique=True)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=True)
    website_link = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120), nullable=True)
    Show = db.relationship('Show', backref ='artist',lazy = True)

    def __repr__(self):
        return f'<artist {self.id} {self.name}>'
class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key =True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    start_time = db.Column(db.DateTime, nullable = False)
    def __repr__(self):
            return f'<show {self.id} {self.artist_id} {self.venue_id}>'
