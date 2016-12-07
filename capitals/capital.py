from datetime import datetime
from google.cloud import datastore


class Capital:

    def __init__(self):
        self.ds = datastore.Client(project="hackathon-team-016")
        self.kind = "Capital"

    def store_capitals(self, tbd):
        key = self.ds.key(self.kind)
        entity = datastore.Entity(key)

        entity['tbd'] = tbd
        entity['timestamp'] = datetime.utcnow()

        return self.ds.put(entity)

    def fetch_capitals(self):
        query = self.ds.query(kind=self.kind)
        query.order = ['-timestamp']
        return self.get_query_results(query)

    def get_query_results(self, query):
        results = list()
        for entity in list(query.fetch()):
            results.append(dict(entity))
        return results

