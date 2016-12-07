import json
import logging
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS 
from google.cloud import datastore

app = Flask(__name__)

@app.route('/')
def hello_world():
    """hello world"""
    return 'Hello World!'

@app.route('/test')
def test():
    return 'Test!'

def __init__(self):
    self.ds = datastore.Client(project="hackathon-team-016")
    self.kind = "Countries16"

@app.route('/country/insert', methods=['PUT'])
def insert_country():
    ds = datastore.Client(project="hackathon-team-016")
    kind = "Countries16"
    key = ds.key(kind)
    entity = datastore.Entity(key)

    name = request.get_json()['name']
    countryCode = request.get_json()['countryCode']
    country = request.get_json()['country']
    countryid = request.get_json()['id']
    latitude = request.get_json()['location']['latitude']
    longitude = request.get_json()['location']['longitude']
    continent = request.get_json()['continent']

    entity.update(
        {
            'name':name,
            'countryCode':countryCode,
            'country':country,
            'id':countryid,
            'continent':continent
        }
    )

    logging.info("Satya - before put")

    resp = make_response(ds.put(entity), 200)
    logging.info("Satya - after put")

    return  resp

@app.route('/country', methods=['GET'])
def list_countries():
    ds = datastore.Client(project="hackathon-team-016")
    kind = "Countries16"

    query = ds.query(kind=kind)
    query.order = ['id']
    
    allCountries = list()
    for entity in list(query.fetch()):
        allCountries.append(dict(entity))
    return allCountries
    
@app.route('/country/id', methods=['GET'])
def fetch_country(id):
    ds = datastore.Client(project="hackathon-team-016")
    kind = "Countries16"

    query = ds.query(kind=kind)
    query.order = ['id']
    return get_query_results(query, id)

@app.route('/country/delete/id', methods=['DELETE'])
def delete_country(self, id):
    ds = datastore.Client(project="hackathon-team-016")
    kind = "Countries16"
    key = ds.key(kind, id)
    entity = datastore.Entity(key)
    entity.delete(key)
    return 200

def get_fetch_results(query, id):
    results = list()
    for entity in list(query.fetch()):
        if entity["id"] == id:
            results.append(dict(entity))
    return results


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500

if __name__ == '__main__':
    # Used for running locally
    app.run(host='127.0.0.1', port=8081, debug=True)
