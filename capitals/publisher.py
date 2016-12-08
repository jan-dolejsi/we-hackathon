#from google.cloud import pubsub
import logging


def publish(id, topicName):
    logging.info('Publishing message {} to topic {}.'.format(id, topicName))

    print('Publishing message {} to topic {}.'.format(id, topicName))
    return
