import unittest
import os
import zlib
import json
import random

from helper import print_func_info
from helper import RAW_TRANSACTIONS_S3_BUCKET, TRANSACTIONS_TABLE_NAME
from helper import TransactionSendFailedException, TransactionNotFoundException
from helper import log, read_file, prepare_invalid_payload, prepare_payload, randomise_ids, randomise_ids_get_sequence_number, randomise_ids_get_sequence_number_set_unitid

from kafka1 import get_kafka_consumer, get_kafka_messages_for_duration, find_kafka_message, send_kafka_message, find_kafka_message_by_primary_entity_id
from rabbit import send_rabbit_transaction


TRANSACTION_VALID_FILE_NAME = "transaction-valid.xml"
CONTROL_TRANSACTION_FILE_NAME = "transaction-control.xml"

TRANSACTION_INVALID_FILE_NAME = "transaction-invalid-xml-tags.xml"
TRANSACTION_INVALID_ID = "6ed62e6db0225dcd5d72b67040350cbc9d3c925f"

STS_RABBITMQ_RETAIL_INPUT_TOPIC = os.getenv("STS_RABBITMQ_RETAIL_INPUT_TOPIC", "SainsburyRetailExport")
STS_RABBITMQ_CONTROL_INPUT_TOPIC = os.getenv("STS_RABBITMQ_CONTROL_INPUT_TOPIC", "SainsburyControlExport")
STS_RABBITMQ_TENDERCONTROL_INPUT_TOPIC = os.getenv("STS_RABBITMQ_TENDERCONTROL_INPUT_TOPIC", "SainsburyTenderControlExport")

class E2ETests(unittest.TestCase):
    @print_func_info
    def test_transaction_sent_to_raw_r10_retail(self):
        try:
            kafka_consumer = get_kafka_consumer("made", "sts-dev-raw-r10-retail-v2")

            r10_xml = read_file(TRANSACTION_VALID_FILE_NAME)
            r10_xml, transaction_id, r10_transaction_id = randomise_ids(r10_xml)
            payload = prepare_payload(r10_xml)

            send_rabbit_transaction(
                queue=STS_RABBITMQ_RETAIL_INPUT_TOPIC,
                payload=payload,
                transaction_id=transaction_id
            )

            found_message = find_kafka_message(kafka_consumer, lambda message: message.value == payload)
            self.assertIsNotNone(found_message)
            kafka_consumer.close()
        except TransactionSendFailedException as e:
            self.fail(e)
        except TransactionNotFoundException as e:
            self.fail(e)

