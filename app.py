import requests
import logging
import json
from flask import Flask, request, render_template
from logging.config import dictConfig


class JSONFormatter(logging.Formatter):
	def __init__(self):
		super().__init__()
	def format(self, record):
		record.msg = json.dumps(record.msg)
		return super().format(record)

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(levelname)s | %(module)s] %(message)s",
                "datefmt": "%B %d, %Y %H:%M:%S %Z",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "worldClock.log",
                "formatter": "default",
            },
            "logtail": {
                "class": "logtail.LogtailHandler",
                "source_token": "qU73jvQjZrNFHimZo4miLdxF",
                "formatter": JSONFormatter(),
            },
        },
        "root": {"level": "DEBUG", "handlers": ["console", "file", "logtail"]},
    }
)

app = Flask(__name__)


@app.route("/")
def home():

    app.logger.info("A user visited the home page")

    return render_template("home.html")


@app.route("/search", methods=["POST"])
def search():

    # Get the search query
    query = request.form["q"]

    app.logger.info("A user performed a search. >>> %s", query)

    # Pass the search query to the Nominatim API to get a location
    location = requests.get(
        "https://nominatim.openstreetmap.org/search",
        {"q": query, "format": "json", "limit": "1"},
    ).json()

    # If a location is found, pass the coordinate to the Time API to get the current time
    if location:

        app.logger.info("A location is found. >>> %s", location)

        coordinate = [location[0]["lat"], location[0]["lon"]]

        time = requests.get(
            "https://timeapi.io/api/Time/current/coordinate",
            {"latitude": coordinate[0], "longitude": coordinate[1]},
        )

        return render_template("success.html", location=location[0], time=time.json())

    # If a location is NOT found, return the error page
    else:

        app.logger.info("A location is NOT found.")

        return render_template("fail.html")
