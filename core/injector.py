from core.llm_helper import LLMAssistant

class PayloadManager:
    def __init__(self, var_context):
        self.var_context = var_context
        self.llm = LLMAssistant()

    def get_payloads(self):
        # Try existing payloads first
        try:
            with open("payloads/injections.txt") as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return self.llm.generate_payloads(self.var_context)







'''
import random
from typing import List, Dict
from core import llm_helper
from graphql import parse, print_ast, visit
from graphql.language import StringValueNode, BooleanValueNode, IntValueNode
import copy

def load_payloads(path: str) -> List[str]:
    with open(path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def mutate_query(query: str, payload: str, variables: dict = None) -> (str, dict):
    # --- Mutate the query AST ---
    try:
        ast = parse(query)

        def visitor_fn(node, *_):
            if isinstance(node, (StringValueNode, BooleanValueNode, IntValueNode)):
                return StringValueNode(value=payload)
            return node

        mutated_ast = visit(ast, visitor_fn)
        mutated_query = print_ast(mutated_ast)
    except Exception as e:
        print(f"[!] AST mutation failed, fallback to string replace: {e}")
        mutated_query = query.replace("PLACEHOLDER", payload)

    # --- Mutate the variables dict ---
    mutated_vars = {}
    if variables:
        mutated_vars = copy.deepcopy(variables)

        def recursive_inject(obj):
            if isinstance(obj, dict):
                return {k: recursive_inject(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [recursive_inject(v) for v in obj]
            elif isinstance(obj, str):
                return payload
            return obj

        mutated_vars = recursive_inject(mutated_vars)

    return mutated_query, mutated_vars

def generate_mutations(parsed_queries: List[Dict], payloads: List[str], limit=3, smart=False) -> List[Dict]:
    mutations = []

    for q in parsed_queries:
        base_query = q['raw']  # Changed from 'query' to 'raw'
        operation = q['name']

        if smart:
            print(f"[LLM] Generating smart payloads for: {operation}")
            generated = llm_helper.generate_contextual_payloads(base_query, operation)
            selected_payloads = generated[:limit] if generated else payloads[:limit]
        else:
            selected_payloads = random.sample(payloads, min(limit, len(payloads)))

        for payload in selected_payloads:
            mutated_query, _ = mutate_query(base_query, payload)
            mutations.append({
                "original_name": operation,
                "mutated_query": mutated_query,
                "payload": payload
            })

    return mutations
'''