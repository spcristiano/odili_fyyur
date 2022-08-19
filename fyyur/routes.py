import sys

from flask import flash, redirect, render_template, request, url_for
from fyyur import db, app
from fyyur.forms import *
from sqlalchemy import func

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    # COMPLETED: replace with real venue data.
    # num_shows should be aggregated based on number of upcoming shows per venue.
    areas = (
            db.session.query(func.count(Venue.id), Venue.city, Venue.state)
            .group_by(Venue.city, Venue.state)
            .all()
    )
    data = []

    for area in areas:
        venuesByArea = (
                Venue.query.filter_by(state = area.state).filter_by(city = area.city).all()
        )
        venueData = []
        for venue in venuesByArea:
            venueData.append(
                    {
                            "id": venue.id,
                            "name": venue.name,
                            "num_upcoming_shows": len(
                                    db.session.query(Show)
                                    .filter(Show.venue_id == 1)
                                    .filter(Show.start_time > datetime.now())
                                    .all()
                                    ),
                            }
                    )
        data.append({"city": area.city, "state": area.state, "venues": venueData})
    return render_template("pages/venues.html", areas = data)


@app.route("/venues/search", methods = ["POST"])
def search_venues():
    # Done: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get("search_term", "")
    results = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    data = []

    for result in results:
        data.append(
                {
                        "id": result.id,
                        "name": result.name,
                        "num_upcoming_shows": len(
                                (
                                        db.session.query(Show)
                                        .filter(Show.venue_id == result.id)
                                        .filter(Show.start_time > datetime.now())
                                        .all()
                                )
                                ),
                        }
                )

    response = {"count": len(data), "data": data}

    return render_template(
            "pages/search_venues.html",
            results = response,
            search_term = request.form.get("search_term", ""),
            )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # Done: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)

    if not venue:
        flash("This venue does not exist." , category="danger")
        return render_template("errors/404.html")

    upcomingShows = []
    pastShows = []
    upcomingShowsNums = set([])
    pastShowsNums = set([])

    for show in (
            db.session.query(Show)
                    .join(Artist)
                    .filter(Show.venue_id == venue_id)
                    .filter(Show.start_time > datetime.now())
                    .all()
    ):
        upcomingShows.append(
                {
                        "artist_id": show.artist_id,
                        "artist_name": show.artist.name,
                        "artist_image_link": show.artist.image_link,
                        "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        }
                )
        upcomingShowsNums.add(show.artist_id)

    for show in (
            db.session.query(Show)
                    .join(Artist)
                    .filter(Show.venue_id == venue_id)
                    .filter(Show.start_time < datetime.now())
                    .all()
    ):
        pastShows.append(
                {
                        "artist_id": show.artist_id,
                        "artist_name": show.artist.name,
                        "artist_image_link": show.artist.image_link,
                        "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        }
                )
        pastShowsNums.add(show.artist_id)

    data = {
            "id": venue.id,
            "name": venue.name,
            "city": venue.city,
            "state": venue.state,
            "address": venue.address,
            "genres": (venue.genres).split(","),
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "upcoming_shows_count": len(upcomingShowsNums),
            "upcoming_shows": upcomingShows,
            "past_shows_count": len(pastShowsNums),
            "past_shows": pastShows,
            }

    return render_template("pages/show_venue.html", venue = data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods = ["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form = form)


@app.route("/venues/create", methods = ["POST"])
def create_venue_submission():
    # Done: insert form data as a new Venue record in the db, instead
    # Done: modify data to be the data object returned from db insertion
    genresList = request.form.getlist("genres")
    venueData = VenueForm(request.form)
    try:
        newVenue = Venue(
                name = venueData.name.data,
                city = venueData.city.data,
                state = venueData.state.data,
                address = venueData.address.data,
                phone = venueData.phone.data,
                genres = ",".join(genresList),
                facebook_link = venueData.facebook_link.data,
                image_link = venueData.image_link.data,
                website = venueData.website.data,
                seeking_talent = venueData.seeking_talent.data,
                seeking_description = venueData.seeking_description.data,
                )
        newVenue.add()
        # on successful db insert, flash success
        flash("Venue: " + newVenue.name + " has been successfully listed!", category="success")
        return render_template("pages/home.html")

    except:
        db.session.rollback()
        print(sys.exc_info())
        # Done: on unsuccessful db insert, flash an error instead.
        flash("An error occurred. Venue " + newVenue.name + " could not be listed.", category="danger")
    finally:
        db.session.close()
        return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods = ["DELETE"])
def delete_venue(venue_id):
    # Done: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        venue = Venue.query.get(venue_id)
        venueName = venue.name
        venue.delete()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button deletes it from the db then redirect the user to the homepage
    if error:
        flash(f"{venueName} venue could not be deleted.", category="danger")

    else:
        flash(f"{venueName} venue has been successfully deleted.", category="success")
    return render_template("pages/home.html")


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # Done: replace with real data returned from querying the database
    data = []
    artists = Artist.query.order_by("id").all()
    for artist in artists:
        data.append({"id": artist.id, "name": artist.name})

    return render_template("pages/artists.html", artists = data)


@app.route("/artists/search", methods = ["POST"])
def search_artists():
    # Done: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get("search_term", "")
    results = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
    data = []

    for result in results:
        data.append(
                {
                        "id": result.id,
                        "name": result.name,
                        "num_upcoming_shows": len(
                                (
                                        db.session.query(Show)
                                        .filter(Show.artist_id == result.id)
                                        .filter(Show.start_time > datetime.now())
                                        .all()
                                )
                                ),
                        }
                )

    response = {"count": len(data), "data": data}

    return render_template(
            "pages/search_artists.html",
            results = response,
            search_term = request.form.get("search_term", ""),
            )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # Done: replace with real artist data from the artists table, using artist_id
    artist = Artist.query.get(artist_id)

    if not artist:
        flash("This artist does not exist.", category="danger")
        return render_template("errors/404.html")

    upcomingShows = []
    pastShows = []

    for show in (
            db.session.query(Show)
                    .join(Venue)
                    .filter(Show.artist_id == artist_id)
                    .filter(Show.start_time > datetime.now())
                    .all()
    ):
        upcomingShows.append(
                {
                        "venue_id": show.venue_id,
                        "venue_name": show.venue.name,
                        "venue_image_link": show.venue.image_link,
                        "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        }
                )

    for show in (
            db.session.query(Show)
                    .join(Venue)
                    .filter(Show.artist_id == artist_id)
                    .filter(Show.start_time < datetime.now())
                    .all()
    ):
        pastShows.append(
                {
                        "venue_id": show.venue_id,
                        "venue_name": show.venue.name,
                        "venue_image_link": show.venue.image_link,
                        "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        }
                )

    data = {
            "id": artist.id,
            "name": artist.name,
            "city": artist.city,
            "state": artist.state,
            "genres": (artist.genres).split(","),
            "phone": artist.phone,
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "upcoming_shows_count": len(upcomingShows),
            "upcoming_shows": upcomingShows,
            "past_shows_count": len(pastShows),
            "past_shows": pastShows,
            }

    return render_template("pages/show_artist.html", artist = data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods = ["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    if not artist:
        flash("This artist does not exist.", category="danger")
        return render_template("errors/404.html")

    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    # Done: populate form with fields from artist with ID <artist_id>
    return render_template("forms/edit_artist.html", form = form, artist = artist)


@app.route("/artists/<int:artist_id>/edit", methods = ["POST"])
def edit_artist_submission(artist_id):
    # Done: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)
    artistData = ArtistForm(request.form)
    genresList = request.form.getlist("genres")
    try:
        artist.name = artistData.name.data
        artist.city = artistData.city.data
        artist.state = artistData.state.data
        artist.phone = artistData.phone.data
        artist.genres = ",".join(genresList)
        artist.facebook_link = artistData.facebook_link.data
        artist.image_link = artistData.image_link.data
        artist.website = artistData.website.data
        artist.seeking_venue = artistData.seeking_venue.data
        artist.seeking_description = artistData.seeking_description.data

        db.session.commit()
        # on successful db update, flash success
        flash("Artist: " + artistData.name.data + " has been successfully updated!", category="success")
    except:
        db.session.rollback()
        print(sys.exc_info())
        # Done: on unsuccessful db update, flash an error instead.
        flash(
                "An error occurred. Artist "
                + artistData.name.data
                + " could not be updated.", category="danger"
                )
    finally:
        db.session.close()
    return redirect(url_for("show_artist", artist_id = artist_id))


@app.route("/venues/<int:venue_id>/edit", methods = ["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    if not venue:
        flash("This venue does not exist.",  category="success")
        return render_template("errors/404.html")

    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    # Done: populate form with values from venue with ID <venue_id>
    return render_template("forms/edit_venue.html", form = form, venue = venue)


@app.route("/venues/<int:venue_id>/edit", methods = ["POST"])
def edit_venue_submission(venue_id):
    # Done: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get(venue_id)
    venueData = VenueForm(request.form)
    genresList = request.form.getlist("genres")
    try:
        venue.name = venueData.name.data
        venue.city = venueData.city.data
        venue.state = venueData.state.data
        venue.address = venueData.address.data
        venue.phone = venueData.phone.data
        venue.genres = ",".join(genresList)
        venue.facebook_link = venueData.facebook_link.data
        venue.image_link = venueData.image_link.data
        venue.website = venueData.website.data
        venue.seeking_talent = venueData.seeking_talent.data
        venue.seeking_description = venueData.seeking_description.data

        db.session.commit()
        # on successful db update, flash success
        flash("Venue: " + venueData.name.data + " has been successfully updated!", category="success")
    except:
        db.session.rollback()
        print(sys.exc_info())
        # Done: on unsuccessful db update, flash an error instead.
        flash(
                "An error occurred. Venue " + venueData.name.data + " could not be updated.",
                category="danger"
                )
    finally:
        db.session.close()
    return redirect(url_for("show_venue", venue_id = venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods = ["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form = form)


@app.route("/artists/create", methods = ["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # Done: insert form data as a new Venue record in the db, instead
    # Done: modify data to be the data object returned from db insertion
    genresList = request.form.getlist("genres")
    artistData = ArtistForm(request.form)
    try:
        newArtist = Artist(
                name = artistData.name.data,
                city = artistData.city.data,
                state = artistData.state.data,
                phone = artistData.phone.data,
                genres = ",".join(genresList),
                facebook_link = artistData.facebook_link.data,
                image_link = artistData.image_link.data,
                website = artistData.website.data,
                seeking_venue = artistData.seeking_venue.data,
                seeking_description = artistData.seeking_description.data,
                )
        newArtist.add()
        # on successful db insert, flash success
        flash("Artist: " + newArtist.name + " has been successfully listed!", category="success")
    except:
        db.session.rollback()
        print(sys.exc_info())
        # Done: on unsuccessful db insert, flash an error instead.
        flash("An error occurred. Artist " + newArtist.name + " could not be listed.",
              category="danger")
    finally:
        db.session.close()
        return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    # Done: displays list of shows at /shows
    data = []
    for show in db.session.query(Show).join(Artist).join(Venue).all():
        data.append(
                {
                        "venue_id": show.venue_id,
                        "venue_name": show.venue.name,
                        "artist_id": show.artist_id,
                        "artist_name": show.artist.name,
                        "artist_image_link": show.artist.image_link,
                        "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        }
                )
    return render_template("pages/shows.html", shows = data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form = form)


@app.route("/shows/create", methods = ["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # Done: insert form data as a new Show record in the db, instead

    showData = ShowForm(request.form)
    try:
        newShow = Show(
                start_time = showData.start_time.data,
                artist_id = showData.artist_id.data,
                venue_id = showData.venue_id.data,
                )
        newShow.add()
        # on successful db insert, flash success
        flash("Show has been successfully listed!", category="success")
    except:
        db.session.rollback()
        print(sys.exc_info())
        # Done: on unsuccessful db insert, flash an error instead.
        flash("An error occurred. Show could not be listed.", category="danger")
    finally:
        db.session.close()
        return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
            Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
            )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")
