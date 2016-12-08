import logging
import json
from google.cloud import datastore
from google.cloud import pubsub
from flask import Flask, request, jsonify, make_response, render_template
import main

def publish(id, topicName):
    logging.info('Publishing message {} to topic {}.'.format(id, topicName))
    #print('Publishing message {} to topic {}.'.format(id, topicName))

    ds = datastore.Client(project="hackathon-team-016")
    kind = "Countries16"

    query = ds.query(kind=kind)
    query.order = ['id']
    result = main.get_fetch_results(query, id)
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

    topic_project_name = topicName.split("/")[1]
    pubsub_client = pubsub.Client(topic_project_name)

    topicName = topicName.split("/")[3]
    topic = pubsub_client.topic(topicName)

    #print 'Topic {}.'.format(topic.full_name)
    #print('Postin {}.'.format(json.dumps(capitalObj)))

    message_id = topic.publish(json.dumps(capitalObj))

    #print "done sending message {}".format(message_id)

    return make_response(jsonify({"messageId": long(message_id)}))

