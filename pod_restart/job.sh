#!/bin/bash
function apply_kafka_connect_configs {
    pip install -r requirements.txt
    python3 task_watcher.py --username c --password c
}

apply_kafka_connect_configs