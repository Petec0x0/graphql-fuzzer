import json
from pathlib import Path
from tqdm import tqdm
from core.utils import load_config, save_results, generate_dummy_value
from core.parser import QueryParser
from core.injector import PayloadManager
from core.executor import GraphQLExecutor

def main(config_path="config/test_case.yaml"):
    # Load configuration
    config = load_config(config_path)
    
    # Parse all operations
    with open("queries/graphql_queries.txt") as f:
        raw_query = f.read()
    
    
    parser = QueryParser(raw_query)
    operations = parser.extract_operations()
    results = []
    executor = GraphQLExecutor(config)

    # Process each operation individually
    for op in tqdm(operations, desc="Processing operations"):
        # Skip anonymous queries if they require variables
        if not op['name'] and op['variables']:
            continue
            
        # Generate dummy variables for this operation
        dummy_vars = {
            var['name']: generate_dummy_value(var['type'])
            for var in op['variables']
        }

        # Fuzz each variable in this operation
        for target_var in op['variables']:
            target_var["operation"] = op['source']
            payload_manager = PayloadManager(target_var)
            payloads = payload_manager.get_payloads()
            
            for payload in payloads:
                # Clone and inject payload
                test_vars = dummy_vars.copy()
                test_vars[target_var['name']] = payload
                
                # Send individual operation
                result = executor.send(
                    query=op['source'],
                    variables=test_vars,
                    payload=payload
                )
                results.append(result)
    
    # Save results
    output_file = save_results(results)
    print(f"\nScan complete! Results saved to {output_file}")

if __name__ == "__main__":
    main()
