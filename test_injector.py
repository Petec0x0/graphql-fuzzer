from core import parser, injector

parsed_queries = parser.parse_all("queries/graphql_queries.txt")
payloads = injector.load_payloads("payloads/injections.txt")

mutations = injector.generate_mutations(parsed_queries, payloads, smart=True)

for m in mutations:
    print(f"Original Operation: {m['original_name']}")
    print("Payload:", m["payload"])
    print("Mutated Query:\n", m["mutated_query"][0])
    print("-" * 50)
