from flask import Flask, request, render_template, Response
import requests
import time
from prometheus_client import start_http_server, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

SEARCH_REQUESTS_TOTAL = Counter('search_requests_total', 'Total number of search requests.')
SEARCH_REQUESTS_DURATION = Histogram('search_request_duration_seconds', 'Duration of /search requests in seconds.')

def record_search_duration(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        SEARCH_REQUESTS_DURATION.observe(duration)
        return result
    return wrapper

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/search", methods=["POST"])
@record_search_duration
def search():
    SEARCH_REQUESTS_TOTAL.inc()
    query = request.form["q"]
    location = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": query, "format": "json", "limit": "1"},
    ).json()

    if location:
        coordinate = [location[0]["lat"], location[0]["lon"]]
        time_data = requests.get(
            "https://timeapi.io/api/Time/current/coordinate",
            params={"latitude": coordinate[0], "longitude": coordinate[1]},
        ).json()

        return render_template("success.html", location=location[0], time=time_data)
    else:
        return render_template("fail.html")

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':

    # Run the Flask application
    app.run('0.0.0.0',debug=True)
