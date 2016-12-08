import json
import logging
import time
from flask import Flask, request, jsonify, make_response, render_template
from flask_cors import CORS 
from google.cloud import datastore
import publisher
from google.cloud import storage, exceptions
from google.cloud.storage import Blob

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('main.html')

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
    """hello team 16"""
    return 'Hello Team 16!'

@app.route('/api/status')
def status():
    return jsonify({
        "insert": True,
        "fetch": True,
        "delete": True,
        "list": True,
        "pubsub": True,
        "storage": False,
        "query": True,
        "search": True
        })

def __init__(self):
    self.ds = datastore.Client(project="hackathon-team-016")
    self.kind = "Countries16"

@app.route('/api/capitals/<int:id>', methods=['PUT'])
def insert_country(id):
    name = request.get_json()['name']
    countryCode = request.get_json()['countryCode']
    country = request.get_json()['country']
    latitude = request.get_json()['location']['latitude']
    longitude = request.get_json()['location']['longitude']
    continent = request.get_json()['continent']
        
    dsClient = datastore.Client(project="hackathon-team-016")
    kind = "Countries16"
    entitykey = dsClient.key(kind, id)
    entity = datastore.Entity(key=entitykey)

    entity.update(
        {
            'name':name,
            'countryCode':countryCode,
            'country':country,
            'id':id,
            'continent':continent,
            'latitude':latitude,
            'longitude':longitude
        }
    )

    logging.info(entitykey)
    logging.info(entity)
    dsClient.put(entity)
    
    return make_response('done')

@app.route('/api/capitals', methods=['GET'])
def list_countries():
    
    queryparam = request.args.get('query', '')
    searchparam = request.args.get('search', '')
      
    dsClient = datastore.Client(project="hackathon-team-016")
    kind = "Countries16"

    query = dsClient.query(kind=kind)
    allCountries = list()
    queryResults = list()

    # No parameters - all data
    if queryparam == "" and searchparam == "":
        queryResults = list(query.fetch())
    # Query parameter 
    elif queryparam != "":
        pos = queryparam.find(":")
        prop = queryparam[:pos]
        v = queryparam[pos+1:]
        if (prop == "id"):
            val = int(v)
        elif prop == "latitude" or prop == "longitude":
            val = float(v)
        else:
            val = v
        query.add_filter(prop, "=", val)
        queryResults = list(query.fetch())
    # Search parameter
    elif searchparam != "":
        for entity in list(query.fetch()):
            if str(entity["id"]) == searchparam or entity['name'] == searchparam or entity['country'] == searchparam or entity['countryCode'] == searchparam or entity['continent'] == searchparam or str(entity['latitude'])== searchparam or str(entity['longitude']) == searchparam:
                queryResults.append(dict(entity))
        
    # Final Formatting of data into JSON with Locations
    for entity in queryResults:
        allCountries.append(dict(entity))

    data = []
    for entity in allCountries:
        item = {}
        geoloc = {}
        geoloc['latitude'] = entity['latitude']
        geoloc['longitude'] = entity['longitude']
        item['id'] = entity['id']
        item['country'] = entity['country']
        item['name'] = entity['name']
        item['location'] = geoloc
        item['countryCode'] = entity['countryCode']
        item['continent'] = entity['continent']
        data.append(item)

    jsonCapitals = json.dumps(data)
    return jsonCapitals
    
@app.route('/api/capitals/<int:id>', methods=['GET'])
def fetch_country(id):
    ds = datastore.Client(project="hackathon-team-016")
    kind = "Countries16"

    query = ds.query(kind=kind)
    query.order = ['id']
    result = get_fetch_results(query, id)
    if len(result) == 0:
        return make_response("Capital not found", 404)

    entity = result[0]
    geolocation = {}
    geolocation['latitude'] = entity['latitude']
    geolocation['longitude'] = entity['longitude']

    capitalObj = {}
    capitalObj['id'] = entity['id']
    capitalObj['country'] = entity['country']
    capitalObj['name'] = entity['name']
    capitalObj['location'] = geolocation
    capitalObj['countryCode'] = entity['countryCode']
    capitalObj['continent'] = entity['continent']

    return jsonify(capitalObj)

@app.route('/api/capitals/<int:id>/store', methods=['POST'])
def store_country(id):
    bucketName = request.get_json()['bucket']
    if bucketName[0:4] != "gs://":
        bucketName = "gs://" + bucketName

    # Fetch entity with id
    ds = datastore.Client(project="hackathon-team-016")
    kind = "Countries16"
    query = ds.query(kind=kind)
    query.order = ['id']
    result = get_fetch_results(query, id)
    if len(result) == 0:
        return make_response("Capital not found", 404)
    entity = result[0]

    # Check if the bucket exists
    gcs = storage.Client(project="hackathon-team-016")

    try:
        bucket = gcs.get_bucket(bucketName)
        filename = "capitalentity.txt"
        
        # Write capital object to a file
        with open(filename, 'w') as outfile:
            json.dump(entity, outfile, sort_keys = True, indent = 4, ensure_ascii = False, separators=(',', ':'))

        # Upload file to the bucket
        blob = Blob(filename, bucket)
        try:
            with open(filename, 'rb') as input_file:
                blob.upload_from_file(input_file)
                return make_response("Stored", 200)
        except IOError:
            return make_response('Error: Cannot find the file {}'.format(filename), 405)
                
    except exceptions.NotFound:
        return make_response('Error: Bucket {} does not exist.'.format(bucketName), 404)
    except exceptions.BadRequest:
        return make_response('Error: Invalid bucket name {}'.format(bucketName), 400)
    except exceptions.Forbidden:
        return make_response('Error: Forbidden, Access denied for bucket {}'.format(bucketName), 403)


@app.route('/api/capitals/<int:id>', methods=['DELETE'])
def delete_country(id):
    client = datastore.Client(project="hackathon-team-016")
    kind = "Countries16"
        
    if isinstance(id, int) == False:
        logging.info("input not int")
        return make_response("Unexpected error", 500)

    #Fetch entity with id
    query = client.query(kind=kind)
    query.add_filter('id', "=", id)
    entities = list(query.fetch())
    if len(entities) > 0:
        entity = entities[0]
        deleteKey = entity.key
        
        logging.info(deleteKey)
        logging.info(entity)
        logging.info("Satya - Delete using key")   
        client.delete(deleteKey)

        time.sleep(1)   #1 second delay to allow delete to happen before the test program checks it with GET
        return "deleted"
    else:
        return make_response("Capital record not found", 404)

def get_fetch_results(query, id):
    results = list()
    for entity in list(query.fetch()):
        if entity["id"] == id:
            results.append(dict(entity))
    return results

@app.route('/api/capitals/<int:id>/publish', methods=['POST'])
def publish_capital(id):
    topic = request.get_json()['topic']
   
    return publisher.publish(id, topic)

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    #return 'An internal error occurred.', 500
    return make_response('Unexpected error', 500)

        
if __name__ == '__main__':
    # Used for running locally
    app.run(host='127.0.0.1', port=8081, debug=True)
