from graphql import parse, print_ast

class QueryParser:
    def __init__(self, query):
        self.ast = parse(query)
        self.operations = []

    def extract_operations(self):
        """Separate queries/mutations and their variables"""
        for definition in self.ast.definitions:
            if definition.kind == 'operation_definition':
                operation = {
                    'name': definition.name.value if definition.name else None,
                    'type': definition.operation,
                    'source': print_ast(definition),
                    'variables': []
                }

                # Extract variables
                for var_def in definition.variable_definitions:
                    operation['variables'].append({
                        'name': var_def.variable.name.value,
                        'type': print_ast(var_def.type)
                    })

                self.operations.append(operation)
        return self.operations