import time
import certifi
import uuid
import os
import datetime
import logging
import sys

from kafka1 import KafkaProducer, KafkaConsumer, TopicPartition
from kafka.errors import NoBrokersAvailable
from kafka.structs import OffsetAndMetadata


kafka_bootstrap_servers = {
    "made": os.getenv("MADE_KAFKA_BOOTSTRAP_SERVERS", "kafka-apps2-1.eu-west-1.dev.deveng.systems:9093,kafka-apps2-2.eu-west-1.dev.deveng.systems:9093,kafka-apps2-3.eu-west-1.dev.deveng.systems:9093")
}

kafka_registry_address = os.getenv("MADE_KAFKA_REGISTRY_ADDRESS", "https://schema-registry-dev.service.eu-west-1.dev.deveng.systems")

kafka_security_protocol = os.getenv("KAFKA_SECURITY_PROTOCOL", "SSL")

consumer_group_id_suffix = uuid.uuid4().hex  # this allows executions to run in parallel


DLQ_TOPIC = os.getenv("DLQ_TOPIC")
REPLAY_TOPIC = os.getenv("REPLAY_TOPIC")
ENV = os.getenv("ENV")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP")
SECRET_PATH = os.getenv("SECRET_PATH")


class TransactionSendFailedException(Exception):
    pass


class TransactionNotFoundException(Exception):
    pass


def log(message):
    print(str(datetime.datetime.now()) + ": " + str(message), flush=True)

def get_kafka_consumer(topic, consumer_group):
    brokers = kafka_bootstrap_servers["made"]
    max_retries = 60
    retry = 0
    while True:
        try:
            log("get_kafka_consumer")
            log("Connecting to the MADE kafka cluster (attempt #" + str(retry) + ")")
            log(brokers)
            log(consumer_group)
            log(get_kafka_cert_filename())
            log(get_kafka_key_filename())
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=brokers,
                enable_auto_commit=False,
                security_protocol=kafka_security_protocol,
                ssl_cafile=certifi.where(),
                ssl_certfile=get_kafka_cert_filename(),
                ssl_keyfile=get_kafka_key_filename(),
                auto_offset_reset="latest",
                group_id=consumer_group,
                consumer_timeout_ms=5000,
                request_timeout_ms=30000
            )
            break
        except NoBrokersAvailable as e:
            retry += 1
            time.sleep(retry)
            if retry == max_retries:
                log("Unable to connect to MADE kafka cluster using brokers " + brokers + " after " + str(retry) + " attempts")
                raise e
    return consumer

def get_kafka_partition_consumer(consumer_group):
    brokers = kafka_bootstrap_servers["made"]
    max_retries = 60
    retry = 0
    while True:
        try:
            log("get_kafka_partition_consumer")
            log("Connecting to the MADE kafka cluster (attempt #" + str(retry) + ")")
            log(brokers)
            log(consumer_group)
            log(get_kafka_cert_filename())
            log(get_kafka_key_filename())
            consumer = KafkaConsumer(
                bootstrap_servers=brokers,
                enable_auto_commit=False,
                security_protocol=kafka_security_protocol,
                ssl_cafile=certifi.where(),
                ssl_certfile=get_kafka_cert_filename(),
                ssl_keyfile=get_kafka_key_filename(),
                auto_offset_reset="earliest",
                group_id=consumer_group,
                consumer_timeout_ms=5000,
                request_timeout_ms=30000
            )
            break
        except NoBrokersAvailable as e:
            retry += 1
            time.sleep(retry)
            if retry == max_retries:
                log("Unable to connect to MADE kafka cluster using brokers " + brokers + " after " + str(retry) + " attempts")
                raise e
    return consumer


def replay():
    consumer = get_kafka_consumer(DLQ_TOPIC, CONSUMER_GROUP)
    producer = get_kafka_producer()
    topic_partition_consumer = get_kafka_partition_consumer(CONSUMER_GROUP)
    partition_offsets = get_latest_offsets(consumer, DLQ_TOPIC)
    replay_messages(REPLAY_TOPIC, topic_partition_consumer, producer, partition_offsets)

def replay_e2e(dlq_topic, replay_topic, consumer_group):
    consumer = get_kafka_consumer(dlq_topic, consumer_group)
    producer = get_kafka_producer()
    topic_partition_consumer = get_kafka_partition_consumer(consumer_group)
    partition_offsets = get_latest_offsets(consumer, dlq_topic)
    replay_messages(replay_topic, topic_partition_consumer, producer, partition_offsets)


def get_latest_offsets(consumer,topic):
    partitions = []
    consumer.topics()
    topic_partitions = consumer.partitions_for_topic(topic)
    for partition in topic_partitions:
        partitions.append(TopicPartition(topic, partition))
    end_offsets = consumer.end_offsets(partitions)
    return end_offsets


def replay_messages(topic, consumer, producer, partition_offsets):
    try:
        log(partition_offsets)
        total_messages = 0
        for partition, offset in partition_offsets.items():
            log(partition)
            log("latest offset:  " + str(offset))
            partitions = [partition]
            consumer.assign(partitions)
            count = 0
            for message in consumer:
                if message.offset < offset and message is not None:
                    message_size = len(message.value)
                    if message_size > 100:
                        producer.send(topic, key=message.key, value=message.value, headers=message.headers, partition=message.partition)
                        count = count + 1
                    consumer.commit({partition: OffsetAndMetadata(message.offset+1, None)})
                else: break
            producer.flush()
            log(str(count) + " transactions have been replayed from " + str(partition))
            total_messages = total_messages + count
    except Exception as e:
        log(e)
    finally:
        if consumer is not None:
            consumer.close()
        if producer is not None:
            producer.close()
    log(str(total_messages) + " transactions have been replayed total")

def get_kafka_cert_filename():
    suffix = get_cert_key_suffix()
    cert_filename = SECRET_PATH + "/sts-client-" + suffix + ".crt"
    # log(cert_filename)
    return cert_filename


def get_kafka_key_filename():
    suffix = get_cert_key_suffix()
    key_file_name = SECRET_PATH + "/sts-client-" + suffix + ".key"
    # log(key_file_name)
    return key_file_name

def get_cert_key_suffix():
    if ENV == "prd":return ENV
    else: return "dev"

def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers=kafka_bootstrap_servers["made"],
        acks="all",
        security_protocol=kafka_security_protocol,
        ssl_cafile=certifi.where(),
        ssl_certfile=get_kafka_cert_filename(),
        ssl_keyfile=get_kafka_key_filename()
    )

if DLQ_TOPIC is not None: log("DLQ_TOPIC: " + DLQ_TOPIC)
if REPLAY_TOPIC is not None: log("REPLAY_TOPIC: " + REPLAY_TOPIC)
if ENV is not None: log("ENV: " + ENV)
if CONSUMER_GROUP is not None: log("CONSUMER_GROUP: " + CONSUMER_GROUP)
if SECRET_PATH is not None: log("SECRET_PATH: " + SECRET_PATH)

if DLQ_TOPIC is not None and REPLAY_TOPIC is not None and CONSUMER_GROUP is not None: replay()

