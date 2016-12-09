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

@app.route("/countries")
def index():
    return render_template('countries.html')

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
    return render_template('countries.html')

@app.route('/api/sortedlist', methods=['GET'])
def sorted_unique_list():
    dsClient = datastore.Client(project="hackathon-team-016")
    kind = "Countries16"
    query = dsClient.query(kind=kind)
    query.distinct_on = ['country']
    query.order = ['country']

    allCountries = list()
    queryResults = query.fetch()
    for entity in queryResults:
        allCountries.append(dict(entity))

    return json.dumps(allCountries)

@app.route('/api/status')
def status():
    return jsonify({
        "insert": True,
        "fetch": True,
        "delete": True,
        "list": True,
        "pubsub": True,
        "storage": True,
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
        # Fire 7 queries for each column and append the results
        results1 = list()
        query1 = dsClient.query(kind=kind)
        query1.add_filter("id", "=", searchparam)
        results1 = list(query1.fetch())

        results2 = list()
        query2 = dsClient.query(kind=kind)
        query2.add_filter("name", "=", searchparam)
        results2 = list(query2.fetch())

        results3 = list()
        query3 = dsClient.query(kind=kind)
        query3.add_filter("country", "=", searchparam)
        results3 = list(query3.fetch())

        results4 = list()
        query4 = dsClient.query(kind=kind)
        query4.add_filter("countryCode", "=", searchparam)
        results4 = list(query4.fetch())

        results5 = list()
        query5 = dsClient.query(kind=kind)
        query5.add_filter("continent", "=", searchparam)
        results5 = list(query5.fetch())

        results6 = list()
        query6 = dsClient.query(kind=kind)
        query6.add_filter("latitude", "=", searchparam)
        results6 = list(query6.fetch())

        results7 = list()
        query7 = dsClient.query(kind=kind)
        query7.add_filter("longitude", "=", searchparam)
        results7 = list(query7.fetch())

        queryResults = results1 + results2 + results3 + results4 + results5 + results6 + results7

        # Get all records and filter on column values
        # for entity in list(query.fetch()):
        #     if str(entity["id"]) == searchparam or entity['name'] == searchparam or entity['country'] == searchparam or entity['countryCode'] == searchparam or entity['continent'] == searchparam or str(entity['latitude'])== searchparam or str(entity['longitude']) == searchparam:
        #         queryResults.append(dict(entity))
        
    # Final Formatting of data into JSON with Locations
    i = 1
    for entity in queryResults:
        allCountries.append(dict(entity))
        i = i+1
        if i > 20:
            break

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
    # result = get_fetch_results(query, id)
    query.add_filter('id', "=", id)
    results = list()
    for entity in list(query.fetch()):
        results.append(dict(entity))
    
    if len(results) == 0:
        return make_response("Capital not found", 404)

    entity = results[0]
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

    logging.info('Storing capital {} to bucket {}.'.format(id, bucketName))
    
    # Fetch entity with id
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

    jsonObj = json.dumps(capitalObj)

    gcs = storage.Client(project="hackathon-team-016")

    try:
        # Check if the bucket exists
        bucket = gcs.get_bucket(bucketName)
        
        #store json to bucket
        filename = str(id)
        blob = Blob(filename, bucket)
        try:
            data = jsonObj.encode('utf-8')
            blob.upload_from_string(data, content_type='text/plain')
            logging.info("File " + filename + " stored in bucket " + bucketName)
            return make_response("Successfully stored in GCS", 200)
        except :
            return make_response('Error: Cannot store json object', 404)
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

        time.sleep(1)   #1 second delay to allow delete to happen before the GET

        # try to get the deleted record to ensure it is deleted - try 3 times
        numtries = 0
        query = client.query(kind=kind)
        query.add_filter('id', "=", id)
        while numtries < 4:
            results = list()
            for entity in list(query.fetch()):
                results.append(dict(entity))
            if len(results) != 0:
                numtries = numtries + 1
            else:
                break

        return make_response("deleted", 200)
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
