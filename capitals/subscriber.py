from google.cloud import pubsub
from pprint import pprint
from inspect import getmembers

pubsub_client_publisher = pubsub.Client("hackathon-team-016")
topic = pubsub_client_publisher.topic("hack_test")

pubsub_client_receiver = pubsub.Client("hackathon-team-016")

subscriptions = pubsub_client_receiver.list_subscriptions()
for sub1 in subscriptions:
    print(sub1.full_name)

#subscription = topic.subscription("groovy-subscription1")    # 
subscription = pubsub.subscription.Subscription("test-subscription", topic)
if not subscription.exists():
    subscription.create(pubsub_client_receiver)

print('Subscription {} created on topic {}.'.format(
    subscription.full_name, topic.full_name))

while True:
    pulled = subscription.pull()

    print 'Received messages'

    for ack_id, message in pulled:
        try:
            print 'Received message {}'.format(ack_id)
        except Exception as e:
            print 'Error {}'.format(e.message)
        else:
            subscription.acknowledge([ack_id])
