import queue, collections, heapq, array, copy, enum, string
import numbers, math, decimal, fractions, random
import numpy as np
import argparse, json
from typing import List, Tuple
from collections import deque

# Question 1
def dfs_search(dct) -> List[Tuple[int, int]]:
    # YOUR CODE HERE. Do not change the name of the function.
    # Dictionary: {cols, rows, obstacles, start, goals}
    start = tuple(dct['start'])
    goals = {tuple(goal) for goal in dct['goals']}
    obstacles = {tuple(obstacle) for obstacle in dct['obstacles']}

    frontier = [start]
    reached = {start}
    parentMap = {start: None}

    if start in obstacles:
        return []

    while frontier:
        curr = frontier.pop()
        if curr in goals:
            path = []
            while curr is not None:
                path.append(curr)
                curr = parentMap[curr]
            return path[::-1]
        # Up, Down, Left, Right
        directions = [(curr[0] - 1, curr[1]), (curr[0] + 1, curr[1]), (curr[0], curr[1] - 1), (curr[0], curr[1] + 1)]
        for dir in directions:
            if (0 <= dir[0] < dct['rows'] and 0 <= dir[1] < dct['cols']) and dir not in obstacles and dir not in reached:
                frontier.append(dir)
                reached.add(dir)
                parentMap[dir] = curr
    return []

# Question 3
def bfs_search(dct) -> List[Tuple[int, int]]:
    # YOUR CODE HERE. Do not change the name of the function.
    start = tuple(dct['start'])
    goals = {tuple(goal) for goal in dct['goals']}
    obstacles = {tuple(obstacle) for obstacle in dct['obstacles']}

    frontier = deque()
    frontier.append(start)
    reached = {start}
    parentMap = {start: None}

    if start in obstacles:
        return []
    
    while frontier:
        curr = frontier.popleft()
        if curr in goals:
            path = []
            while curr is not None:
                path.append(curr)
                curr = parentMap[curr]
            return path[::-1]
        # Up, Down, Left, Right
        directions = [(curr[0] - 1, curr[1]), (curr[0] + 1, curr[1]), (curr[0], curr[1] - 1), (curr[0], curr[1] + 1)]
        for dir in directions:
            if (0 <= dir[0] < dct['rows'] and 0 <= dir[1] < dct['cols']) and dir not in obstacles and dir not in reached:
                frontier.append(dir)
                reached.add(dir)
                parentMap[dir] = curr
    return []

# Question 5
def ucs_search(dct) -> List[Tuple[int, int]]:
    # YOUR CODE HERE. Do not change the name of the function.
    start = tuple(dct['start'])
    goals = {tuple(goal) for goal in dct['goals']}
    obstacles = {tuple(obstacle) for obstacle in dct['obstacles']}

    frontier = []
    heapq.heappush(frontier, (0, start))
    reached = {start: 0}
    parentMap = {start: None}

    if start in obstacles:
        return []
    
    while frontier:
        cost, curr = heapq.heappop(frontier)
        if curr in goals:
            path = []
            while curr is not None:
                path.append(curr)
                curr = parentMap[curr]
            return path[::-1]
        # Up, Down, Left, Right
        directions = [(curr[0] - 1, curr[1]), (curr[0] + 1, curr[1]), (curr[0], curr[1] - 1), (curr[0], curr[1] + 1)]
        for dir in directions:
            if (0 <= dir[0] < dct['rows'] and 0 <= dir[1] < dct['cols']) and dir not in obstacles:
                if (dir not in reached or cost + 1 < reached[dir]):
                    heapq.heappush(frontier, (cost + 1, dir))
                    reached[dir] = cost + 1
                    parentMap[dir] = curr
    return []        


parser = argparse.ArgumentParser(description="Run DFS with a JSON file input.")
parser.add_argument("json_file", type=str, help="Path to the JSON file")
args = parser.parse_args()
with open(args.json_file, "r") as file:
    data = json.load(file)
print('start:', data['start'], 'goals:', data['goals'])
print(ucs_search(data))


