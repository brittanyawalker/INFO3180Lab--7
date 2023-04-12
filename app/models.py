from datetime import datetime
import pytz

from . import db


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text)
    poster = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('US/Eastern')))

    def __repr__(self):
        return f"<Movie {self.title}>"
