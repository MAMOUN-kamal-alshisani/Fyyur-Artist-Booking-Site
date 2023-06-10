#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for ,jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
app.app_context().push()

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0000@localhost:5432/fyyur'
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
    
    # "past_shows": [],
    # "upcoming_shows": [],
    # "past_shows_count": 0,
    # "upcoming_shows_count": 0,
class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120),nullable=True)
    genres = db.Column(db.ARRAY(db.String(120)),nullable=False)
    website_link = db.Column(db.String(120),nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120),nullable=True)
    Show = db.relationship('Show', backref ='venue',lazy = True)

    def __repr__(self):
        return f'<venue {self.id} {self.name}>'
    # facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=True)
    website_link = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120), nullable=True)
    Show = db.relationship('Show', backref ='artist',lazy = True)

    def __repr__(self):
        return f'<artist {self.id} {self.name}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
migrate = Migrate(app, db)
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.



class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key =True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    start_time = db.Column(db.DateTime, nullable = False)
    def __repr__(self):
            return f'<show {self.id} {self.artist_id} {self.venue_id}>'
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
        date = dateutil.parser.parse(value)
        if format == 'full':
         format="EEEE MMMM, d, y 'at' h:mma"
        elif format == 'medium':
         format="EE MM, dd, y h:mma"
        return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
# db.create_all()

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.

  data = []
  dataList = Venue.query.with_entities(Venue.city,Venue.state,Venue.id,Venue.name).all()

  for list in dataList:  
    upcoming_shows = db.session.query(Show).filter(Show.venue_id == list.id ).filter(Show.start_time > datetime.now()).all()
    data.append(
        {
            "city":list.city ,
            "state":list.state ,
            "venues": [{
      "id": list.id,
      "name":list.name,
      "num_upcoming_shows": len(upcoming_shows),
    }]
     })
   
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
 search_venue = request.form.get('search_term') 

 filtered_list = db.session.query(Venue).with_entities(Venue.name,Venue.id).filter(Venue.name.like(f"%{search_venue}%")).all()
 
 count = db.session.query(Venue).with_entities(Venue.name,Venue.id).filter(Venue.name.like(f"%{search_venue}%")).count()
    
 response = {}
 response["count"] = count
 response['data'] = []
 for list in filtered_list:
  upcoming_shows =len(db.session.query(Show).filter(Show.venue_id == list.id ).filter(Show.StartTime > datetime.now()).all())

  data= {
           "id": list.id,
           "name": list.name,
           "num_upcoming_shows": upcoming_shows,
    }

  response['data'].append(data)
 return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

 venue = db.session.query(Venue).with_entities(Venue.id,Venue.name,Venue.genres,Venue.address,Venue.city,Venue.state,Venue.phone,Venue.website_link,
                Venue.facebook_link,
                Venue.seeking_talent,
                Venue.seeking_description,
               Venue.image_link).filter(Venue.id == venue_id).one()

 past_shows = db.session.query(Show).filter(Show.venue_id == venue_id ).filter(Show.start_time < datetime.now()).count()
 upcoming_shows = db.session.query(Show).filter(Show.venue_id == venue_id ).filter(Show.start_time > datetime.now()).count()

 data = {
     "id": venue.id,
    "name": venue.name,
    "genres":venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows_count": past_shows,
    "upcoming_shows_count": upcoming_shows,
    'past_shows': [],
    'upcoming_shows':[]
}

 past_shows_len =db.session.query(Show).filter(Show.venue_id == venue_id ).filter(Show.start_time < datetime.now())

 for show in past_shows_len:
    artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()
    data['past_shows'].append({
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link":artist.image_link,
      "start_time": show.start_time.strftime('%m/%d/%Y')
    })
  
#   #prepare list of upcoming shows
 upcoming_shows_len =db.session.query(Show).filter(Show.venue_id == venue_id ).filter(Show.start_time > datetime.now())

 for show in upcoming_shows_len:
    data['upcoming_shows'].append({
  "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link":artist.image_link,
      "start_time": show.start_time.strftime('%m/%d/%Y')
    })

 return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
 
  # TODO: insert form data as a new Venue record in the db, instead
     seeking_talent = '' 
     if request.form.get('seeking_talent') == 'y':
      seeking_talent = True
     else:  seeking_talent = False

     name = request.form.get('name')
     city = request.form.get('city')
     state = request.form.get('state')
     address = request.form.get('address')
     phone = request.form.get('phone')
     genres = request.form.get('genres')
     image_link = request.form.get('image_link')
     facebook_link = request.form.get('facebook_link')
     website_link = request.form.get('website_link')     
     seeking_description = request.form.get('seeking_description')
     venue = Venue(
          name=name,
          city=city,
          state=state,
          address=address,
          phone=phone,
          genres=genres,
          image_link=image_link,
          facebook_link=facebook_link,
          website_link=website_link,
          seeking_talent=seeking_talent,
          seeking_description=seeking_description
)
  # TODO: modify data to be the data object returned from db insertion
     try:
          db.session.add(venue)
          db.session.commit()
     except Exception  as e:
       db.session.rollback()
       print('error occurred!', e) 
     finally:
              db.session.close()
              flash('Venue ' + request.form.get('name') + ' was successfully listed!')
              return render_template('pages/home.html')
     
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
   record = db.session.query(Venue).get(venue_id)

   try:
        #  record = db.session.query(Venue).get(venue_id)
         db.session.query(Venue).delete(record)
         db.session.query(Show).delete(record)

         db.session.commit()
   except Exception  as e:
       db.session.rollback()
       print('error occurred!', e) 
   finally:
              db.session.close()
              flash('Venue ' + record.name + ' was successfully removed!')
              return render_template('pages/home.html')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  dataList = Artist.query.with_entities(Artist.id,Artist.name).all()
  for list in dataList:
        
    data.append({
      "id": list.id,
      "name":list.name,
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
     response = {}

     search_venue = request.form.get('search_term') 
     print(search_venue)
     filtered_list = db.session.query(Artist) \
             .with_entities(Artist.name,Artist.id) \
             .filter(Artist.name.like(f"%{search_venue}%")).all()
 
     count = db.session.query(Artist) \
             .with_entities(Artist.name,Artist.id) \
             .filter(Artist.name.like(f"%{search_venue}%")).count()
    
     response["count"] = count
     response['data'] = []
     for list in filtered_list:
         upcoming_shows =len(db.session.query(Show).filter(Show.venue_id == list.id ).filter(Show.start_time > datetime.now()).all())

         data= {
           "id": list.id,
           "name": list.name,
           "num_upcoming_shows": upcoming_shows,
           }
    
         response['data'].append(data)
  
     return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

     
  

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
 artist = db.session.query(Artist).with_entities(Artist.id,Artist.name,Artist.genres,Artist.city,Artist.state,Artist.phone,Artist.website_link,
        Artist.facebook_link,
        Artist.seeking_venue,
        Artist.seeking_description,
        Artist.image_link).filter(Artist.id == artist_id).one()
 
 past_shows = db.session.query(Show).filter(Show.artist_id == artist_id ).filter(Show.start_time < datetime.now()).count()
 upcoming_shows = db.session.query(Show).filter(Show.artist_id == artist_id ).filter(Show.start_time > datetime.now()).count()


 data = {
     "id": artist.id,
    "name": artist.name,
    "genres":artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows_count": past_shows,
    "upcoming_shows_count": upcoming_shows,
    "past_shows":[],
     "upcoming_shows":[]
}

 past_shows_len =db.session.query(Show).filter(Show.artist_id == artist_id ).filter(Show.start_time < datetime.now())

 for show in past_shows_len:
    # artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()
    data['past_shows'].append({
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link":artist.image_link,
      "start_time": show.start_time.strftime('%m/%d/%Y')
    })
 upcoming_shows_len =db.session.query(Show).filter(Show.artist_id == artist_id ).filter(Show.start_time > datetime.now())

 for show in upcoming_shows_len:
    data['upcoming_shows'].append({
     "venue_id": show.artist_id,
      "venue_name": artist.name,
      "venue_image_link":artist.image_link,
      "start_time": show.start_time.strftime('%m/%d/%Y')
    })

  

 return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  Artist = Artist.query.get(artist_id)
 
  artist={
    "id": Artist.id,
    "name": Artist.name,
    "genres": Artist.genres,
    "city": Artist.city,
    "state": Artist.state,
    "phone": Artist.phone,
    "website": Artist.website,
    "facebook_link": Artist.facebook_link,
    "seeking_venue": Artist.seeking_venue,
    "seeking_description": Artist.seeking_description,
    "image_link": Artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

     Artist = Artist.query.get(artist_id)
     Artist.name = request.form.get('name')
     Artist.city = request.form.get('city')
     Artist.state = request.form.get('state')
     Artist.phone = request.form.get('phone')
     Artist.genres = request.form.get('genres')
     Artist.image_link = request.form.get('image_link')
     Artist.facebook_link = request.form.get('facebook_link')
     Artist.website_link = request.form.get('website_link') 
     Artist.seeking_venue = request.form.get('seeking_venue') 
     Artist.seeking_description = request.form.get('seeking_description')
     return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  Artist = Artist.query.get(venue_id)
    
  venue={
    "id": Artist.id,
    "name": Artist.name,
    "genres": Artist.genres,
    "city": Artist.city,
    "state": Artist.state,
    "address":Artist.address,
    "phone": Artist.phone,
    "website": Artist.website,
    "facebook_link": Artist.facebook_link,
    "seeking_talent": Artist.seeking_talent,
    "seeking_description": Artist.seeking_description,
    "image_link": Artist.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
     Artist = Artist.query.get(venue_id)
     Artist.name = request.form.get('name')
     Artist.city = request.form.get('city')
     Artist.state = request.form.get('state')
     Artist.address = request.form.get('address')
     Artist.phone = request.form.get('phone')
     Artist.genres = request.form.get('genres')
     Artist.image_link = request.form.get('image_link')
     Artist.facebook_link = request.form.get('facebook_link')
     Artist.website_link = request.form.get('website_link')     
     Artist.seeking_description = request.form.get('seeking_description')
     return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
     seeking_venue = '' 
     if request.form.get('seeking_venue') == 'y':
      seeking_venue = True
     else:  seeking_venue = False

     name = request.form['name']
     city = request.form['city']
     state = request.form['state']
     phone = request.form['phone']
     genres = request.form['genres']
     image_link = request.form['image_link']
     facebook_link = request.form['facebook_link']
     website_link = request.form['website_link'] 
     seeking_description = request.form['seeking_description']
     artist = Artist(
          name=name,
          city=city,
          state=state,
          # address=address,
          phone=phone,
          genres=genres,
          image_link=image_link,
          facebook_link=facebook_link,
          website_link=website_link,
          seeking_venue=seeking_venue,
          seeking_description=seeking_description
)
    #  print(artist)
     db.session.add(artist)
     try:
          db.session.commit()
     except Exception  as e:
      #  db.session.rollback()
       print('error occurred!', e) 
     finally:
              db.session.close()
              flash('Venue ' + request.form.get('name') + ' was successfully listed!')
              return render_template('pages/home.html')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
 shows = db.session.query(Show).with_entities(Show.id,Show.artist_id, Show.venue_id, Show.start_time).all()
#  shows_start_time = db.session.query(Show).with_entities(Show.id,Show.artist_id, Show.venue_id, Show.start_time).one()

 data=[]
 for show in shows:
      artists = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()
      venues = db.session.query(Venue).filter(Venue.id == show.venue_id).one()
 data.append({
    "venue_id": venues.id,
    "venue_name": venues.name,
    "artist_id": venues.id,
    "artist_name": artists.name,
    "artist_image_link":artists.image_link,
    "start_time": str(show.start_time)
  })

 return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():

  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = request.form.get('start_time')
  show = Show(
     artist_id = artist_id,
     venue_id = venue_id,
     start_time = start_time
  )
  try:
          db.session.add(show)
          db.session.commit()
  except Exception  as e:
       db.session.rollback()
       print('error occurred!', e) 
  finally:
  # on successful db insert, flash success
       flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
       return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
