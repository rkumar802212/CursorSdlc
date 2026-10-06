"""Local run entry: Flask debug is always False (D10 / security lock)."""

from dotenv import load_dotenv

from flight_search import create_app

load_dotenv()
app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
