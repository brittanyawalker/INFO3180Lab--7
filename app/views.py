"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""
import os
from flask import Flask, jsonify, render_template, request, send_from_directory, make_response
from flask_wtf.csrf import generate_csrf
from werkzeug.utils import secure_filename

from app.forms import MovieForm
from app.models import Movies
from . import db

app = Flask(__name__)

# Set the path for file uploads
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

###
# Routing for your application.
###

@app.route('/')
def index():
    return jsonify(message="This is the beginning of our API")

@app.route('/api/v1/movies', methods=['POST'])
def add_movie():
    form = MovieForm(request.form)
    if form.validate():
        title = form.title.data
        desc = form.description.data
        poster = form.poster.data
        pname = secure_filename(poster.filename)

        new_movie = Movies(title=title, description=desc, poster=pname)
        db.session.add(new_movie)
        db.session.commit()

        poster.save(os.path.join(app.config['UPLOAD_FOLDER'], pname))
        response = {
            "message": "Movie successfully added",
            "title": title,
            "poster": pname,
            "desc": desc
        }
        return jsonify(response), 201
    else:
        errors = form_errors(form)
        return make_response(jsonify(errors=errors), 400)

@app.route('/api/v1/movies', methods=['GET'])
def get_movies():
    movies = Movies.query.all()
    response = {"movies": []}
    for movie in movies:
        movie_info = {
            "id": movie.id,
            "title": movie.title,
            "poster": f'/api/v1/posters/{movie.poster}',
            "description": movie.description
        }
        response['movies'].append(movie_info)
    return jsonify(response)

@app.route('/api/v1/posters/<filename>')
def get_poster(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/v1/csrf-token', methods=['GET'])
def get_csrf_token():
    return jsonify({'csrf_token': generate_csrf()})

# Define a function to collect form errors from Flask-WTF
def form_errors(form):
    errors = []
    for field, errors in form.errors.items():
        for error in errors:
            message = "Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            )
            errors.append(message)
    return errors

# Define a custom 404 page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Add headers to response to disable caching
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
