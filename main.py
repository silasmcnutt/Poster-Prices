from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/get_price", methods=["GET"])
def get_price():
    """
    GET /get_price?url=<full_movie_url>

    Extracts the movie ID from the provided URL, fetches the price, and returns it as JSON.
    """

    movie_url = request.args.get("url")
    if not movie_url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    try:
        # Extract movie ID from the URL
        path = urlparse(movie_url).path
        if not path.startswith("/products/"):
            return jsonify({"error": "Invalid movie URL"}), 400

        movie_id = path.split("/products/")[-1]

        url = f"https://www.movieposters.com/products/{movie_id}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)

        if res.status_code != 200:
            return jsonify({"error": "Movie not found"}), 404

        soup = BeautifulSoup(res.text, "html.parser")
        price_span = soup.select_one(".pdp__price")

        if not price_span:
            return jsonify({"error": "Price not found"}), 404

        price = price_span.text.strip()
        return jsonify({"id": movie_id, "price": price})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
