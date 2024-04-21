import subprocess
import requests
import time
import subprocess
import re
import pandas as pd

# Configuration for Prometheus
prometheus_pod_query = 'avg(sum(rate(container_cpu_usage_seconds_total{namespace="default", pod=~"teastore-webui-.*", container!="POD", container!=""}[5m])) by (pod))' 
prometheus_node_query = '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle", instance="10.224.0.6:9100"}[5m])) * 100)'
prometheus_url = 'http://localhost:9090'
replica_count = 1

# Define your test stages
stages = [
    {'vus': 200, 'duration': '10s'},
    {'vus': 500, 'duration': '10s'},
    {'vus': 1500, 'duration': '120s'},
    {'vus': 2000, 'duration': '120s'},
    {'vus': 2500, 'duration': '120s'},
    {'vus': 3000, 'duration': '120s'},
    {'vus': 3500, 'duration': '120s'},
    {'vus': 4000, 'duration': '120s'},
    {'vus': 4500, 'duration': '120s'}
]

def query_prometheus(query):
    """Query Prometheus using the HTTP API and return the JSON response."""
    try:
        # Construct the full URL for the query endpoint
        full_url = f"{prometheus_url}/api/v1/query"
        # Make the GET request to the Prometheus query endpoint
        response = requests.get(full_url, params={'query': query})
        # Raise an exception if the request failed
        response.raise_for_status()
        # Parse the JSON response
        data = response.json()
        return data
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Error querying Prometheus: {err}")
    except ValueError as err:
        print(f"Error parsing JSON response: {err}")


def run_stage(stage):
    """Run a k6 test stage."""
    test_command = f"k6 run --vus {stage['vus']} --duration {stage['duration']} ./k6Job.js"
    print(f"Running stage: {stage}")
    try:
        # result = 
        subprocess.run(test_command, check=True, shell=True, text=True)
        # output = result.stdout
        
        # Parse the output to find the HTTP request failure rate
        # match = re.search(r"http_req_failed[^:]*: (\d+\.\d+)%", output)
        # if match:
        #     failed_rate = match.group(1)
        #     print(f"HTTP Requests Failed: {failed_rate}%")
        # else:
        #     print("Failed to find the HTTP request failure rate in the output.")
        print('Stage complete, querying Prometheus...')
        prometheus_pod_response = query_prometheus(prometheus_pod_query)
        prometheus_node_response = query_prometheus(prometheus_node_query)
        return prometheus_pod_response['data']['result'][0]['value'][1], prometheus_node_response['data']['result'][0]['value'][1], 6969
    except subprocess.CalledProcessError as e:
        print(f'Error running k6 stage: {e}')



def scale_deployment(deployment_name, replicas, namespace="default"):
    try:
        # Constructing the kubectl command
        command = ["kubectl", "scale", "deployment", deployment_name, "--replicas={}".format(replicas), "-n", namespace]
        
        # Executing the command
        subprocess.run(command, check=True)
        print(f"Deployment {deployment_name} scaled to {replicas} replicas in the '{namespace}' namespace.")
    
    except subprocess.CalledProcessError as e:
        print(f"Error scaling deployment: {e}")


"""Orchestrate running of stages and Prometheus queries."""

data_array = []
fail_limit = False
replicas = 10

print("replicas: ", replicas)
scale_deployment("teastore-webui", replicas)
# time.sleep(30)
for stage in stages:
    pod_response, node_response, failed_rate = run_stage(stage)
    data_array.append([replicas, stage['vus'], pod_response, node_response, failed_rate])
    print("fail rate int: ", float(failed_rate))
    # if float(failed_rate) > 50:
    #     fail_limit = True
    #     break
    print("4 minute cool down...")
    # time.sleep(240)


    


headers = ["replicas", "virtual users", "pod response", "node response", "failed rate"]

# Create DataFrame
df = pd.DataFrame(data_array, columns=headers)

# File path
file_path = 'pod_model_results.csv'

# Save to CSV
df.to_csv(file_path, index=False)

print(f"Data written to {file_path}")
        
