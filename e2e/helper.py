import functools
import gzip
import time
import fastavro
import json
import io
import uuid
import random
import re
import datetime
from src.generated import r10_pb2
from src.generated import r10_invalid_pb2
from kafka.errors import NoBrokersAvailable

TEST_XML_DIRECTORY = './src/test/resources'
TEST_XML_PATH = TEST_XML_DIRECTORY + '/*.xml'

DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_DELAY = 5

RAW_TRANSACTIONS_S3_BUCKET = 'sts-raw-transactions-dev'
TRANSACTIONS_TABLE_NAME = 'dev-sts-transactions'

SCHEMA_PATH = './src/test/resources/unaudited.avsc'
parsedSchema = fastavro.parse_schema(json.load(open(SCHEMA_PATH, "r"))) 
# parsedSchema  is a dictionary     parsedSchema["fields"][0] = {'default': None, 'name': 'time_to_live', 'type': ['null', 'long']}

class TransactionSendFailedException(Exception):
    pass
class TransactionNotFoundException(Exception):
    pass

def log(message):
    print(str(datetime.datetime.now()) + ": " + str(message), flush=True)
# log("Kafka")   -->  2023-05-10 17:09:47.050085: Kafka

# TEST_XML_DIRECTORY = './src/test/resources'
def read_file(filename):
    with open(f"{TEST_XML_DIRECTORY}/{filename}", 'r') as f:
        txn = f.read()
        return txn

def randomise_ids_get_sequence_number_set_unitid(xml, unitID):
    sequence_number = str(random.randint(1, 9999))     # 9859
    sequence_number_padded = sequence_number.zfill(4)  # 9859  
    r10_transaction_id = uuid.uuid4().hex              # 0dccdc654b4b4d69ab7a18972ee417c4 
    timestamp = "2018-07-04T07:00:08.5198207"
    xml = re.sub(r"(?s)<SequenceNumber>.*?</SequenceNumber>", r"%s" % "<SequenceNumber>" + sequence_number + "</SequenceNumber>", xml)
    xml = re.sub(r"(?s)<TransactionID>.*?</TransactionID>", r"%s" % "<TransactionID>" + r10_transaction_id + "</TransactionID>", xml)
    xml = re.sub(r"(?s)<EndDateTime>.*?</EndDateTime>", r"%s" % "<EndDateTime>" + timestamp + "+00:00</EndDateTime>", xml)
    xml = re.sub(r"(?s)<EndDateTime r10Ex:Offset.*?</EndDateTime>", r"%s" % "<EndDateTime r10Ex:Offset=\"00:00:00\">" + timestamp + "</EndDateTime>", xml)
    xml = re.sub(r"(?s)<WorkstationID.*?</WorkstationID>", r"%s" % "<WorkstationID WorkstationLocation=\"16\" TypeCode=\"X:KeyboardPOS\">223</WorkstationID>", xml)
    xml = re.sub(r"(?s)<UnitID.*?</UnitID>", r"%s" % "<UnitID r10Ex:SubStore=\"2887\" Name=\"0434 COREYS MILL\">" + unitID + "</UnitID>", xml)

    transaction_id = "629" + unitID + "223" + sequence_number_padded + "00040718070008"
    return (xml, transaction_id, r10_transaction_id, sequence_number)
    '''
        xml = "<SequenceNumber>67</SequenceNumber><TransactionID>2</TransactionID><EndDateTime>344</EndDateTime><WorkstationID>20</WorkstationID><UnitID>100</UnitID>"
        unitID = "0434"

        sequence_number = str(random.randint(1, 9999))     # 9859
        sequence_number_padded = sequence_number.zfill(4)  # 9859  
        r10_transaction_id = uuid.uuid4().hex   
        timestamp = "2018-07-04T07:00:08.5198207"

        Changes to xml:
            <SequenceNumber> sequence_number </SequenceNumber>
            <TransactionID> 10_transaction_id <TransactionID>
            <EndDateTime>2018-07-04T07:00:08.5198207+00:00</EndDateTime>
            <WorkstationID WorkstationLocation="16" TypeCode="X:KeyboardPOS">223</WorkstationID>
            <UnitID r10Ex:SubStore="2887" Name="0434 COREYS MILL">0434</UnitID>
        
        transaction_id = "629" + "0434" + "223" + sequence_number_padded + "00040718070008"    
        r10_transaction_id    
        sequence_number    
            
    '''
def randomise_ids_get_sequence_number(xml):
    return randomise_ids_get_sequence_number_set_unitid(xml, "0434")

def randomise_ids(xml):
    r10_xml, transaction_id, r10_transaction_id, sequence_number = randomise_ids_get_sequence_number(xml)
    return (r10_xml, transaction_id, r10_transaction_id)

def envelope_xml(xml):
    xml_no_declaration = xml.replace("""<?xml version="1.0" encoding="utf-8"?>""", "")
    return """<?xml version="1.0" encoding="utf-8"?>
    <STSEnvelope>
	    <MetaDataList>
		<MetaData Index="0">
		  <Key>FinancialDate</Key>
		  <Value>20200117</Value>
		  <Unknown>N</Unknown>
		</MetaData>
		<MetaData Index="1">
		  <Key>A_TEST_KEY_1</Key>
		  <Value>A_TEST_VALUE_1</Value>
		  <Unknown>AN_UNKNOWN_VALUE_1</Unknown>
		</MetaData>
		<MetaData Index="2">
		  <Key>A_TEST_KEY_2</Key>
		  <Value>A_TEST_VALUE_2</Value>
		  <Unknown>AN_UNKNOWN_VALUE_2</Unknown>
		</MetaData>
	  </MetaDataList>""" + xml_no_declaration + "</STSEnvelope>"

# protoc --proto_path=. --python_out=. ./*.proto
def prepare_payload(xml):
    r10_txn = r10_pb2.Record()
    r10_txn.payloads.xml = xml
    r10_txn.payloads.payloadType = "PayloadTransaction"
    r10_txn.topic = "topic"
    create_metadata(r10_txn.payloads)
    protobuf_serialised = r10_txn.SerializeToString()
    protobuf_compressed = gzip.compress(protobuf_serialised)
    return protobuf_compressed  # Type of protobuf_compressed = bytes
    '''
    print(r10_txn)
    payloads {
        payloadType: "PayloadTransaction"
        metaData {
            key: "FinancialDate"
            value: "20200120"
            unknown: "Unknown"
        }
        xml: "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n    <STSEnvelope>\n\t    <MetaDataList>\n\t\t<MetaData Index=\"0\">\n\t\t  <Key>FinancialDate</Key>\n\t\t  <Value>20200117</Value>\n\t\t  <Unknown>N</Unknown>\n\t\t</MetaData>\n\t\t<MetaData Index=\"1\">\n\t\t  <Key>A_TEST_KEY_1</Key>\n\t\t  <Value>A_TEST_VALUE_1</Value>\n\t\t  <Unknown>AN_UNKNOWN_VALUE_1</Unknown>\n\t\t</MetaData>\n\t\t<MetaData Index=\"2\">\n\t\t  <Key>A_TEST_KEY_2</Key>\n\t\t  <Value>A_TEST_VALUE_2</Value>\n\t\t  <Unknown>AN_UNKNOWN_VALUE_2</Unknown>\n\t\t</MetaData>\n\t  </MetaDataList><SequenceNumber>67</SequenceNumber><TransactionID>2</TransactionID><EndDateTime>344</EndDateTime><WorkstationID>20</WorkstationID><UnitID>100</UnitID></STSEnvelope>"
    }
    '''

def create_metadata(payloads):
    metadata1 = r10_pb2.Record().MetaData()
    metadata1.key = "FinancialDate"
    metadata1.value = "20200120"
    metadata1.unknown = "Unknown"
    payloads.metaData.append(metadata1)

def prepare_invalid_payload(xml):
    r10_txn = r10_invalid_pb2.RecordInvalid()
    r10_txn.payloads.xml = xml
    r10_txn.topic = "topic"
    protobuf_serialised = r10_txn.SerializeToString()
    protobuf_compressed = gzip.compress(protobuf_serialised)
    return protobuf_compressed
    '''
    print(r10_txn)
    topic: "topic"
    payloads {
        xml: "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n    <STSEnvelope>\n\t    <MetaDataList>\n\t\t<MetaData Index=\"0\">\n\t\t  <Key>FinancialDate</Key>\n\t\t  <Value>20200117</Value>\n\t\t  <Unknown>N</Unknown>\n\t\t</MetaData>\n\t\t<MetaData Index=\"1\">\n\t\t  <Key>A_TEST_KEY_1</Key>\n\t\t  <Value>A_TEST_VALUE_1</Value>\n\t\t  <Unknown>AN_UNKNOWN_VALUE_1</Unknown>\n\t\t</MetaData>\n\t\t<MetaData Index=\"2\">\n\t\t  <Key>A_TEST_KEY_2</Key>\n\t\t  <Value>A_TEST_VALUE_2</Value>\n\t\t  <Unknown>AN_UNKNOWN_VALUE_2</Unknown>\n\t\t</MetaData>\n\t  </MetaDataList><SequenceNumber>67</SequenceNumber><TransactionID>2</TransactionID><EndDateTime>344</EndDateTime><WorkstationID>20</WorkstationID><UnitID>100</UnitID></STSEnvelope>"
    }
    '''

def get_avro_message_transaction_id(avro_message):
    # parsedSchema ----->  './src/test/resources/unaudited.avsc'
    record = fastavro.schemaless_reader(io.BytesIO(avro_message), parsedSchema)
    return record["TransactionID"]


'''
DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_DELAY = 5
'''
def retry(retry_count=DEFAULT_RETRY_COUNT, delay=DEFAULT_RETRY_COUNT): 
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            for i in range(retry_count):
                log(f"Retry {f.__name__} attempt {i + 1}")
                try:
                    result = f(*args)
                    log(f"Retry {f.__name__} attempt {i + 1} succeeded")
                    return result
                except Exception as e:
                    if i == retry_count - 1:
                        raise TransactionNotFoundException(f"Transaction {args[1]} not found in {args[0]}: {e}")
                time.sleep(delay)
            raise Exception("Exhausted retries without returning a result or throwing an exception")

        return wrapper

    return decorator


'''
retry() -> 
def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            for i in range(3):    0,1,2
                log(f"Retry {f.__name__} attempt {i + 1}")
                try:
                    result = f(*args)
                    log(f"Retry {f.__name__} attempt {i + 1} succeeded")
                    return result
                except Exception as e:
                    if i == 3 - 1:
                        raise TransactionNotFoundException(f"Transaction {args[1]} not found in {args[0]}: {e}")
                time.sleep(5)
            raise Exception("Exhausted retries without returning a result or throwing an exception")

        return wrapper

    return decorator

retry()(test_adder)
def wrapper(*args, **kwargs):
            for i in range(3):        retry_count = 3 
                log(f"Retry {test_adder.__name__} attempt {i + 1}")
                try:
                    result = test_adder(*args) 
                    log(f"Retry {f.__name__} attempt {i + 1} succeeded")
                    return result
                except Exception as e:
                    if i == 3 - 1:
                        raise TransactionNotFoundException(f"Transaction {args[1]} not found in {args[0]}: {e}")
                time.sleep(3) 
            raise Exception("Exhausted retries without returning a result or throwing an exception")

        return wrapper

R1:
1. Increase retry_count=DEFAULT_RETRY_COUNT.
2. Set an appropriate delay=DEFAULT_RETRY_COUNT value
'''

def print_func_info(func):
    def echo_func_timestamp(*func_args, **func_kwargs):
        log('')
        log('Start {} timestamp: {}'.format(func.__name__, datetime.datetime.now().time()))
        log('')
        try:
            result = func(*func_args, **func_kwargs)
            log('End {} timestamp: {}'.format(func.__name__, datetime.datetime.now().time()))
            return result
        except TransactionNotFoundException as e:
            log('{} - TransactionNotFoundException timestamp: {}'.format(func.__name__, datetime.datetime.now().time()))
            raise TransactionNotFoundException from e
        except TransactionSendFailedException as e:
            log('{} - TransactionSendFailedException timestamp: {}'.format(func.__name__, datetime.datetime.now().time()))
            raise TransactionSendFailedException from e
        except NoBrokersAvailable as e:
            log('{} - NoBrokersAvailable timestamp: {}'.format(func.__name__, datetime.datetime.now().time()))
            raise NoBrokersAvailable from e
        except AssertionError as e:
            log('{} - AssertionError timestamp: {}'.format(func.__name__, datetime.datetime.now().time()))
            raise AssertionError from e

    return echo_func_timestamp




def printZ():
    xml = """<?xml version="1.0" encoding="utf-8"?>"""+"<SequenceNumber>67</SequenceNumber><TransactionID>2</TransactionID><EndDateTime>344</EndDateTime><WorkstationID>20</WorkstationID><UnitID>100</UnitID>"
    (a,b,c,d) = randomise_ids_get_sequence_number_set_unitid(xml, "0434")
    (a,b,c,d) = randomise_ids_get_sequence_number(xml)
    (a,b,c) = randomise_ids(xml)
    x = envelope_xml(xml)
    y = prepare_invalid_payload(x)

    def add(a):
        return a+2

    def test_adder(a,b):
        return a+b

    
    retry()(test_adder)(2,3)
    print_func_info(test_adder)(2,3)
printZ()