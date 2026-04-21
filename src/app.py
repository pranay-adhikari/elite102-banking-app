from flask import Flask
from routes import register_routes
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("KEY")

register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)