import pika
import os
from helper import log
import yaml

from kubernetes import client, config


rabbitmq_host = os.getenv("RABBITMQ_HOST", "sts-rabbitmq-0.sts-rabbitmq-headless.sts.svc.cluster.local")
rabbitmq_user = os.getenv("RABBITMQ_USER", "user")
rabbitmq_pass = os.getenv("RABBITMQ_PASS", "password")


def get_rabbit_connection():
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    parameters = pika.ConnectionParameters(rabbitmq_host, 5672, '/', credentials)
    return pika.BlockingConnection(parameters)

def send_rabbit_transaction(queue, payload, transaction_id):
    log("Sending payload to RabbitMQ, transactionId: " + transaction_id)
    connection = get_rabbit_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    channel.basic_publish(exchange='', routing_key=queue, body=payload)
    connection.close()

print("34")