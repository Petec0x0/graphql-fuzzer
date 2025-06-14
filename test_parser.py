from core import parser

parsed = parser.parse_all("queries/graphql_queries.txt")

for entry in parsed:
    print(f"Operation: {entry['operation']}")
    print(f"Name: {entry['name']}")
    print(f"Fields: {entry['fields']}")
    print("-" * 40)
