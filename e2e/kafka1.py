import time
import certifi
import uuid
import os
from schema_registry.client import SchemaRegistryClient
from schema_registry.serializers import AvroMessageSerializer, JsonMessageSerializer

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import NoBrokersAvailable

def log(message):
    print(str(datetime.datetime.now()) + ": " + str(message), flush=True)
# log("Kafka")   -->  2023-05-10 17:09:47.050085: Kafka

class TransactionSendFailedException(Exception):
    pass

kafka_bootstrap_servers = {
    "epos": os.getenv("EPOS_KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    "made": os.getenv("MADE_KAFKA_BOOTSTRAP_SERVERS", "kafka-apps2-1.eu-west-1.dev.deveng.systems:9093,kafka-apps2-2.eu-west-1.dev.deveng.systems:9093,kafka-apps2-3.eu-west-1.dev.deveng.systems:9093")
}

kafka_registry_address = os.getenv("MADE_KAFKA_REGISTRY_ADDRESS", "https://schema-registry-dev.service.eu-west-1.dev.deveng.systems")

kafka_security_protocol = os.getenv("KAFKA_SECURITY_PROTOCOL", "SSL")

consumer_group_id_suffix = uuid.uuid4().hex  # this allows executions to run in parallel

def get_kafka_cert_filename(cluster):
    if cluster == "made":
        return "secrets/dev/sts-operational.crt"
    else:
        return None

def get_kafka_key_filename(cluster):
    if cluster == "made":
        return "secrets/dev/sts-operational.key"
    else:
        return None
    
def get_kafka_consumer(cluster, topic):
    brokers = kafka_bootstrap_servers[cluster]
    max_retries = 60
    retry = 0
    while True:
        try:
            log("Connecting to " + cluster + " kafka cluster (attempt #" + str(retry) + ")")
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=brokers,
                enable_auto_commit=False,
                security_protocol=kafka_security_protocol,
                ssl_cafile=certifi.where(),
                ssl_certfile=get_kafka_cert_filename(cluster),
                ssl_keyfile=get_kafka_key_filename(cluster),
                auto_offset_reset="latest", 
                group_id="sts-operational-e2e-tests-" + consumer_group_id_suffix,
                consumer_timeout_ms=5000,   # number of millisecond to throw a timeout exception to the consumer if no message is available for consumption. --- > R2
                request_timeout_ms=30000    # It says that the client is going to wait this much time for the server to respond to a request.
            )
            break
        except NoBrokersAvailable as e:
            retry += 1
            time.sleep(retry)
            if retry == max_retries:
                log("Unable to connect to " + cluster + " kafka cluster using brokers " + brokers + " after " + str(retry) + " attempts")
                raise e
    kafka_seek_to_latest(consumer)
    return consumer

def kafka_seek_to_latest(consumer):
    log("Seeking to latest kafka messages")
    get_kafka_messages(consumer, expected_messages=10000, empty_timeout=3)

# Read messages until `expected_messages` is reached and there are no more messages, or no results are returned during `empty_timeout`
def get_kafka_messages(consumer, expected_messages, empty_timeout=120):
    log("Reading messages from Kafka")
    messages = []
    empty_result_start = None
    while True:
        read_messages = False
        for message in consumer:
            read_messages = True
            messages.append(message)
        if len(messages) >= expected_messages:
            break
        elif read_messages:
            empty_result_start = None
        else:
            current_time = time.time()
            if empty_result_start is None:
                empty_result_start = current_time
            elif current_time - empty_result_start > empty_timeout:
                read_messages = len(messages)
                log(f"Read {read_messages} Kafka messages (not waiting for more as {empty_timeout}s timeout was exceeded)")
                break
    return messages

def get_kafka_messages_for_duration(consumer, duration):
    log(f"Reading messages from Kafka for {duration}s")
    messages = []
    start_time = time.time()
    while (time.time() - start_time) < duration:
        for message in consumer:
            messages.append(message)
    return messages


# Read messages until one that matches the comparator is found, or no results are returned during `empty_timeout`
def find_kafka_message(consumer, comparator, empty_timeout=150):
    log("Finding message in Kafka")
    empty_result_start = None
    while True:
        read_messages = False
        for message in consumer:
            read_messages = True
            if comparator(message):
                return message
        if read_messages:
            empty_result_start = None
        else:
            current_time = time.time()
            if empty_result_start is None:
                empty_result_start = current_time
            elif current_time - empty_result_start > empty_timeout:
                break

def find_kafka_message_by_primary_entity_id(consumer, primaryEntityID,  empty_timeout=120):
    log("Finding message in Kafka")
    empty_result_start = None
    while True:
        read_messages = False
        for message in consumer:
            read_messages = True
            decoded_message = decode_avro_message(message.value)
            if primaryEntityID in decoded_message["PrimaryEntityID"]:
                return message
        if read_messages:
            empty_result_start = None
        else:
            current_time = time.time()
            if empty_result_start is None:
                empty_result_start = current_time
            elif current_time - empty_result_start > empty_timeout:
                break


def send_transaction(topic, payload, transaction_id):
    log("Sending payload to Kafka, transactionId: " + transaction_id)
    send_kafka_message(topic, payload)


def send_kafka_message(topic, payload):
    kafka_producer = None
    try:
        kafka_producer = get_kafka_producer()
        kafka_producer.send(topic, payload).get()
        kafka_producer.flush()
    except Exception as e:
        log(e)
        raise TransactionSendFailedException("Failed to send transaction")
    finally:
        if kafka_producer is not None:
            kafka_producer.close()

def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers=kafka_bootstrap_servers["epos"],
        acks="all"
    )

def get_schema_from_registry(subject):
    sr = SchemaRegistryClient(kafka_registry_address)
    return sr.get_schema(subject=subject, version='latest')

def decode_avro_message(avro_message):
    client = SchemaRegistryClient(kafka_registry_address)
    return AvroMessageSerializer(client).decode_message(avro_message)

client = SchemaRegistryClient("http://localhost:8081/")
k = client.get_schema(subject="sts-dev-drs-avro-v1-value", version='latest')
print(k)

def encode_to_avro_message(subject, dict_message):
    client = SchemaRegistryClient(kafka_registry_address)
    return AvroMessageSerializer(client).encode_record_with_schema_id(get_schema_from_registry(subject).schema_id, dict_message)


