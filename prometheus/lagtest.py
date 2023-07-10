import requests  

PROMETHEUS = 'http://kafka2-cluster-topic-metrics-exporter.service.eu-west-1.dev.deveng.systems/prometheus/consumer/offsets'
inst = "kafka2-cluster.+"
group_id='sts-kc-to-snowflake'


PROMQL2 = {'query':'kafka_consumer_group_offset_lag{instance=~"kafka2-cluster.+",groupid="sts-kc-to-snowflake"}'}

r1 = requests.get(url = PROMETHEUS, params = PROMQL2)
print(r1.content)


