import yaml
import json
from pathlib import Path
from datetime import datetime

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def save_results(results, output_dir="results"):
    Path(output_dir).mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/scan_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    return filename

def generate_dummy_value(var_type):
    """Generate type-appropriate dummy values"""
    base_type = var_type.replace('!', '').lower()
    
    type_map = {
        'string': 'dummy_string',
        'boolean': False,
        'int': 42,
        'id': 'dummy_id_123',
        'float': 3.14,
        'url': 'http://dummy.example',
        'host': 'example.com',
        'port': 8080,
        'path': '/dummy/path',
        'scheme': 'https'
    }
    
    # Handle list types (e.g., [String!])
    if base_type.startswith('['):
        inner_type = base_type[1:-1].lower()
        return [type_map.get(inner_type, 'dummy_value')]
    
    return type_map.get(base_type, 'dummy_value')