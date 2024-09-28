import json
import logging

from flask import request, jsonify

from collections import defaultdict, deque

from routes import app

logger = logging.getLogger(__name__)

@app.route('/bugfixer/p1', methods=['POST'])
def evaluate():
    logging.info("data sent for evaluation {}".format(request.get_json()))
    data = request.get_json()
    results = []

    for project_data in data:
        time = project_data['time']
        prerequisites = project_data['prerequisites']

        n = len(time)  
        
        graph = defaultdict(list)
        indegree = [0] * (n + 1)
        total_time = [0] * (n + 1) 

        for a, b in prerequisites:
            graph[a].append(b)
            indegree[b] += 1

        queue = deque()
        for i in range(1, n + 1):
            total_time[i] = time[i - 1]  
            if indegree[i] == 0: 
                queue.append(i)

        while queue:
            current = queue.popleft()

            for neighbor in graph[current]:
                total_time[neighbor] = max(total_time[neighbor], total_time[current] + time[neighbor - 1])
                indegree[neighbor] -= 1
                
                if indegree[neighbor] == 0:
                    queue.append(neighbor)
                    
        results.append(max(total_time))

    logging.info("Final result list: {}".format(results))
    return jsonify(results)
