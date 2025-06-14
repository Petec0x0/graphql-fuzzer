import requests

class GraphQLExecutor:
    def __init__(self, config):
        self.endpoint = config['endpoint']
        self.headers = config.get('headers', {})
        
    def send(self, query, variables, payload):
        """Send request and capture full details"""
        try:
            request_data = {
                'query': query,
                'variables': variables
            }
            
            response = requests.post(
                self.endpoint,
                json=request_data,
                headers=self.headers,
                timeout=10
            )
            
            return {
                "request": request_data,  # Full request capture
                "payload_used": payload,
                "response": {
                    "status": response.status_code,
                    "time": response.elapsed.total_seconds(),
                    "headers": dict(response.headers),
                    "body": response.json()
                }
            }
        except Exception as e:
            return {
                "request": request_data,
                "payload_used": payload,
                "error": str(e)
            }









'''
import requests
import time
from typing import List, Dict

def send_mutation(mutation: Dict, endpoint: str, headers: Dict = {}) -> Dict:
    query = mutation['mutated_query']
    payload = {
        "query": query,
        "variables": {}  # could expand this later
    }

    try:
        start = time.time()
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        elapsed = time.time() - start

        return {
            "status_code": response.status_code,
            "time": round(elapsed, 3),
            "payload": mutation['payload'],
            "operation": mutation['original_name'],
            "response": response.text[:500]  # preview only
        }

    except Exception as e:
        return {
            "status_code": "error",
            "time": 0,
            "payload": mutation['payload'],
            "operation": mutation['original_name'],
            "response": str(e)
        }

def execute_all(mutations: List[Dict], endpoint: str, headers: Dict = {}) -> List[Dict]:
    results = []
    for m in mutations:
        result = send_mutation(m, endpoint, headers)
        print(f"[{result['status_code']}] {result['operation']} | Payload: {result['payload']} | Time: {result['time']}s")
        results.append(result)
    return results
'''