import requests
import uuid
from flask import Flask, request, render_template, session
from logging.config import dictConfig


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(levelname)s | %(module)s] %(message)s",
                "datefmt": "%B %d, %Y %H:%M:%S %Z",
            },
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
                "formatter": "default",
            },
        },
        "root": {"level": "DEBUG", "handlers": ["console", "file", "logtail"]},
    }
)

app = Flask(__name__)

app.secret_key = "c00de22a8b1e4daa2cabc8b3f82fdb753574293f8b673f9a"


@app.route("/")
def home():

    session["ctx"] = {"request_id": str(uuid.uuid4())}

    app.logger.info("A user visited the home page >>> %s", session["ctx"])

    return render_template("home.html")


@app.route("/search", methods=["POST"])
def search():

    # Get the search query
    query = request.form["q"]

    app.logger.info(
        "A user performed a search. | query: %s >>> %s", query, session["ctx"]
    )

    # Pass the search query to the Nominatim API to get a location
    location = requests.get(
        "https://nominatim.openstreetmap.org/search",
        {"q": query, "format": "json", "limit": "1"},
    ).json()

    # If a location is found, pass the coordinate to the Time API to get the current time
    if location:

        app.logger.info(
            "A location is found. | location: %s >>> %s", location, session["ctx"]
        )

        coordinate = [location[0]["lat"], location[0]["lon"]]

        time = requests.get(
            "https://timeapi.io/api/Time/current/coordinate",
            {"latitude": coordinate[0], "longitude": coordinate[1]},
        )

        return render_template("success.html", location=location[0], time=time.json())

    # If a location is NOT found, return the error page
    else:

        app.logger.info("A location is NOT found. >>> %s", session["ctx"])

        return render_template("fail.html")


@app.after_request
def logAfterRequest(response):

    app.logger.info(
        "path: %s | method: %s | status: %s | size: %s >>> %s",
        request.path,
        request.method,
        response.status,
        response.content_length,
        session["ctx"],
    )

    return response
