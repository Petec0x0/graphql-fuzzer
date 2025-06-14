import re
import os
import requests
import logging

class LLMAssistant:
    def __init__(self, base_url="http://192.168.1.80:11434"):
        self.api_url = f"{base_url}/api/chat"
        
    def generate_payloads(self, var_context):
        """Generate context-aware payloads using LLM"""
        prompt = f"""Generate 20 fuzzing payloads for a GraphQL variable with:
                - Name: {var_context['name']}
                - Type: {var_context['type']}
                - Operation: {var_context['operation']}

                Focus on {var_context['type']}-specific vulnerabilities. Return "ONLY" payloads separated by newlines in a code block (no bullet point/numbering)."""
        
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": "deepseek-r1:32b",
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False
            })
            content = response.json()['message']['content']
            print("####################### LLM #######################", content)
            
            # Extract the payloads from the code block
            match = re.search(r'```(?:[^\n]*)\n([\s\S]*?)```', content)
            if match:
                payload_block = match.group(1)
                payloads = [line.strip() for line in payload_block.strip().splitlines() if line.strip()]
                self._save_payloads(payloads)
                print("####################### PAYLOADS #######################", payloads)
                return payloads
            else:
                logging.warning("No code block found in LLM response.")
                return []
        except Exception as e:
            logging.error(f"LLM Error: {str(e)}")
            return []

    def _save_payloads(self, payloads):
        """Save generated payloads to injections.txt"""
        filepath = "payloads/injections.txt"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        existing = set()
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                existing = set(line.strip() for line in f)

        with open(filepath, "a") as f:
            for p in payloads:
                if p not in existing:
                    f.write(f"{p}\n")