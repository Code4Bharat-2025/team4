from flask import Flask

def create_app():
    app = Flask(__name__)
    return app.run(host="0.0.0.0", port=80, debug=True)

create_app()