# test_executor.py
from core import parser, injector, executor

parsed = parser.parse_all('queries/graphql_queries.txt')
payloads = injector.load_payloads('payloads/injections.txt')
mutations = injector.generate_mutations(parsed, payloads, limit=3, smart=False)

target_endpoint = "http://127.0.0.1:5013/graphql"
custom_headers = {
    "Authorization": "Bearer YOUR-TOKEN-HERE"  # optional
}

results = executor.execute_all(mutations, target_endpoint, headers=custom_headers)

# Optional: Save for review
import json
with open("fuzz_results.json", "w") as f:
    json.dump(results, f, indent=2)
