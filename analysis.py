# analysis.py (corrected)
import json
from collections import defaultdict

class ResultAnalyzer:
    def __init__(self, result_file):
        with open(result_file) as f:
            self.results = json.load(f)
        
        self.metrics = defaultdict(lambda: {
            'total': 0, 'vulnerable': 0, 
            'types': defaultdict(int)
        })

    def detect_vulnerability(self, entry):
        """Heuristic-based vulnerability detection"""
        res = entry['response']
        payload = entry['payload_used']
        
        # 1. Error-based detection
        if res['status'] >= 500:
            return ('SERVER_ERROR', 'High')
        if 'error' in entry:
            return ('ERROR', 'Medium')
            
        # 2. Payload reflection detection (fixed)
        body_str = str(res.get('body', ''))
        if payload in body_str:
            return ('REFLECTION', 'High')
            
        # 3. Time-based detection
        if res.get('time', 0) > 1.0:  # Custom threshold
            return ('TIMING', 'Medium')
            
        # 4. Empty response detection
        if not res.get('body'):
            return ('EMPTY_RESPONSE', 'Low')
            
        return (None, None)

    def generate_metrics(self):
        for entry in self.results:
            # Extract operation type (query/mutation)
            first_word = entry['request']['query'].split()[0]
            op_type = first_word if first_word in ('query', 'mutation') else 'other'
            
            vuln_type, confidence = self.detect_vulnerability(entry)
            
            self.metrics[op_type]['total'] += 1
            if vuln_type:
                self.metrics[op_type]['vulnerable'] += 1
                self.metrics[op_type]['types'][vuln_type] += 1
        
        return dict(self.metrics)

# Usage
if __name__ == "__main__":
    analyzer = ResultAnalyzer("results/scan_20250602_141920.json")
    metrics = analyzer.generate_metrics()
    print(json.dumps(metrics, indent=2))