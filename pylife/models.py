from pylife import db
from sqlalchemy.sql import func


class Zone(db.Model):
    __tablename__ = "zones"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    points = db.Column(db.Text, nullable=False)


class House(db.Model):
    __tablename__ = "houses"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    owner = db.Column(db.String(22), nullable=True)
    price = db.Column(db.Float, nullable=True)
    expiry = db.Column(db.DateTime, nullable=True)
    last_update = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class Blip(db.Model):
    __tablename__ = "blips"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.Text, nullable=False)
