import os
import requests
import json
from time import sleep
import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

env_name = os.environ['ENV_NAME']
subdomain_suffix = "prd" if env_name == "prd" else "nonprd"
pushgateway_url = f"http://pushgateway.grada-pii-sales-{subdomain_suffix}.js-devops.co.uk/metrics/job"

def manage_tasks():
    pass

def post_metric(url, group, key, value):
    try:
        return requests.post(f"{url}/{group}", data=f"{key} {value}\n")
    except requests.ConnectionError:
        logger.error("ConnectionError while pushing metrics to Pushgateway")


if __name__=='__main__':
    await_duration=5*60
    while True:
        try:
            logger.info("Managing tasks...")
            manage_tasks()
            post_metric(pushgateway_url, f"kafka_connect_manager", "CONNECT_MANAGER_FAILURE", 0)
        except Exception as e:
            post_metric(pushgateway_url, "kafka_connect_manager", "CONNECT_MANAGER_FAILURE", 1)
            logger.error(f"Failed to manage tasks due to exception: \n\t {str(e)}")
        logger.info(f"Completed task management cycle... Next cycle in {await_duration} seconds")
        sleep(await_duration)