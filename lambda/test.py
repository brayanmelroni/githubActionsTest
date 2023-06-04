try:

    import json
    import sys
    import requests
    print("All imports ok ...")
except Exception as e:
    print("Error Imports : {} ".format(e))


def lambda_handler(event, context):
    print("Hello AWS!")
    print("event = {}".format(event))
    return {
        'statusCode': 200,
    }

#  https://github.com/soumilshah1995/PythonLambdaDockerECR                    https://www.youtube.com/watch?v=2VtuNOEw8S4
# curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d "{\"msg\":\"hello\"}"

