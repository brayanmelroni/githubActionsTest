import requests
import json
from time import sleep
import logging
import argparse

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger()

def manage_tasks(connector, connector_status, kafka_connect_url,username, password):
    failed_tasks = [ task for task in connector_status['tasks'] if task['state'] == 'FAILED']
    unassigned_tasks = [ task for task in connector_status['tasks'] if task['state'] == 'UNASSIGNED']
    logger.info(f"Failed tasks: {[ t['id'] for t in failed_tasks]}")
    logger.info(f"Unassigned tasks: {[ t['id'] for t in unassigned_tasks]}")
    for task in failed_tasks + unassigned_tasks :
        task_id = task['id']
        if kafka_connect_url :
            logger.info(f"Restarting task: {task_id} for connector {connector}")
            req = requests.post(
                f"{kafka_connect_url}/connectors/{connector}/tasks/{task_id}/restart",auth=(f"{username}", f"{password}"))
            logger.info(f"Received status: {req.status_code} response: {req.text}")
        else:
            logger.error("Could not get or resolve kafka_connect_url")


def manage_unassigned_failed_connector(connector, kafka_connect_url, username, password):
    if kafka_connect_url:
        logger.info(f"Restarting connector: {connector} with url {kafka_connect_url}")
        req = requests.post(
            f"{kafka_connect_url}/connectors/{connector}/restart",auth=(f"{username}", f"{password}"))
        logger.info(f"Received status: {req.status_code} response: {req.text}")

def manage_connectors(kafka_connect_url,username, password):
    connectors = json.loads(requests.get(f"{kafka_connect_url}/connectors",auth=(f"{username}", f"{password}")).text)
    for connector in connectors:
        logger.info(f"Managing connector: {connector}")
        connector_status = json.loads(requests.get(f"{kafka_connect_url}/connectors/{connector}/status",auth=(f"{username}", f"{password}")).text)
        connector_state = connector_status['connector']['state']

        if connector_state == 'RUNNING':
            manage_tasks(connector, connector_status, kafka_connect_url,username,password)
        elif connector_state == 'UNASSIGNED' or connector_state == 'FAILED':
            logger.warning(f"Connector {connector} is in {connector_state} state")
            manage_unassigned_failed_connector(connector, kafka_connect_url,username,password)
        elif connector_state == 'PAUSED':
            logger.warning(f"Will skip connector {connector} because it has been PAUSED")
        else:
            pass
            logger.warning(f"Unmanaged state: {connector_state} found for connector: {connector}, skipping...")

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='kafka-connect task manager',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--username', help='username', default='connect')
    parser.add_argument('--password', help='password')
    args = parser.parse_args()
    username = args.username
    password = args.password
    print(username, password)

    kafka_connect_url = f"http://localhost:8083"
    await_duration=5
    while True:
        try:
            logger.info("Managing tasks...")
            manage_connectors(kafka_connect_url,username,password)
        except Exception as e:
            logger.error(f"Failed to manage tasks due to exception: \n\t {str(e)}")
        logger.info(f"Completed task management cycle... Next cycle in {await_duration} seconds")
        sleep(await_duration)