import json
import logging
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS 
from google.cloud import datastore

app = Flask(__name__)

@app.route('/parsejson')
def parse_json():
    with open('countries.json') as data_file:    
        data = json.load(data_file)
    mystring = "Start:"
    for country in data:
        mystring = mystring + "Countries,"
        for attribute, value in country.iteritems():
            mystring = mystring + attribute + ":" + str(value) + ", " 
    return mystring
    
@app.route('/')
def hello_world():
    """hello world"""
    return 'Hello World!'

@app.route('/api/status')
def status():
    return jsonify({
        "insert": True,
        "fetch": True,
        "delete": False,
        "list": True,
        "pubsub": False,
        "storage": False,
        "query": False,
        "search": False
        })

def __init__(self):
    self.ds = datastore.Client(project="hackathon-team-016")
    self.kind = "Countries16"

@app.route('/api/capitals/<int:id>', methods=['PUT'])
def insert_country(id):
    ds = datastore.Client(project="hackathon-team-016")
    kind = "Countries16"
    key = ds.key(kind)
    entity = datastore.Entity(key)

    name = request.get_json()['name']
    countryCode = request.get_json()['countryCode']
    country = request.get_json()['country']
    countryid = id
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
    returnVal = ds.put(entity)
    logging.info("Satya - after put")

    return make_response('done')

@app.route('/api/capitals', methods=['GET'])
def list_countries():
    ds = datastore.Client(project="hackathon-team-016")
    kind = "Countries16"

    query = ds.query(kind=kind)
    query.order = ['id']
    
    allCountries = list()
    for entity in list(query.fetch()):
        allCountries.append(dict(entity))
    return jsonify(allCountries)
    
@app.route('/api/capitals/<int:id>', methods=['GET'])
def fetch_country(id):
    ds = datastore.Client(project="hackathon-team-016")
    kind = "Countries16"

    query = ds.query(kind=kind)
    query.order = ['id']
    result = get_fetch_results(query, id)
    return jsonify(result)

@app.route('/api/capitals/<int:id>', methods=['DELETE'])
def delete_country(id):
    client = datastore.Client(project="hackathon-team-016")
    kind = "Countries16"
    key = client.key(kind, str(id))
    
    logging.info(key)
    logging.info("Satya - delete using client")
    client.delete(key)
    
    #Fetch entity with id
    query = client.query(kind=kind)
    query.add_filter('id', "=", id)
    entity = query.fetch()
    logging.info(entity)
    logging.info("Satya - Delete using entity")
    entity.delete()

    return "deleted"

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
