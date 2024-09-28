import json
import logging
import heapq

from flask import request

from collections import defaultdict, deque

from routes import app

logger = logging.getLogger(__name__)

@app.route('/bugfixer/p2', methods=['POST'])
def evaluate():
    logging.info("data sent for evaluation {}".format(request.get_json()))
    data = request.get_json()
    results = []


    def max_bugsfixed(bugseq):
        bugseq.sort(key=lambda x: x[1])
        
        total_time = 0
        heap = []
        
        for difficulty, limit in bugseq:
            logger.log(logging.INFO, heap)
            if total_time + difficulty <= limit:
                heapq.heappush(heap, -difficulty)  # Push negative value for max-heap behavior
                total_time += difficulty
            elif heap and -heap[0] > difficulty:
                total_time += difficulty + heapq.heappop(heap)  # Remove the hardest (largest) bug
                heapq.heappush(heap, -difficulty)
        
        return len(heap)
    
    for bug_data in data:
        bugseq = bug_data['bugseq']
        max_bug = max_bugsfixed(bugseq)
        results.append(max_bug)
    
    logging.info("Final result list: {}".format(results))
    return json.dumps(results)
