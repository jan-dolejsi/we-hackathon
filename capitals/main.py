import logging
import json
import base64

from flask import Flask
from flask_cors import CORS


app = Flask(__name__)

@app.route('/')
def hello_world():
    """hello world"""
    return 'Hello World!'

@app.route('/test')
def test():
    return 'Test!'

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500

if __name__ == '__main__':
    # Used for running locally
    app.run(host='127.0.0.1', port=8081, debug=True)
