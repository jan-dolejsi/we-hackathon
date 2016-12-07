import json
from datetime import datetime
from google.cloud import datastore


class Capital:

    def __init__(self):
        self.ds = datastore.Client(project="hackathon-team-016")
        self.kind = "Countries16"

    @app.route('/country/insert', methods=['PUT'])
    def insert_country(self):
        key = self.ds.key(self.kind)
        entity = datastore.Entity(key)

        name = request.get_json()['name']
        countryCode = request.get_json()['countryCode']
        country = request.get_json()['country']
        countryid = request.get_json()['id']
        latitude = request.get_json()['latitude']
        longitude = request.get_json()['longitude']
        continent = request.get_json()['continent']

        entity['name'] = name
        entity['countryCode'] = countryCode
        entity['country'] = country
        entity['id'] = countryid
        entity['location'] = [latitude, longitude]
        entity['continent'] = continent
        
        #return self.ds.put(entity)
        return 200

    @app.route('/country', methods=['GET'])
    def list_countries(self):
        query = self.ds.query(kind=self.kind)
        query.order = ['id']
        
        allCountries = list()
        for entity in list(query.fetch()):
            allCountries.append(dict(entity))
        return allCountries
        
    @app.route('/country/id', methods=['GET'])
    def fetch_country(self, id):
        query = self.ds.query(kind=self.kind)
        query.order = ['id']
        return self.get_query_results(query, id)

    @app.route('/country/id', methods=['DELETE'])
    def delete_country(self, id):
        key = self.ds.key(self.kind, id)
        entity = datastore.Entity(key)
        entity.delete(key)
        return 200

    def get_fetch_results(self, query, id):
        results = list()
        for entity in list(query.fetch()):
            if entity["id"] == id:
                results.append(dict(entity))
        return results