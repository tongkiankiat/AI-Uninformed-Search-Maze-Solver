import heapq
from enum import Enum
import argparse, json

def search(dct) -> list[int]:
    # YOUR CODE HERE. Do not change the name of the function.
    # Dictionary:{cols, rows, obstacles, creeps, start, goals, num_flash_left, num_nuke_left}
    # Encoding for actions
    class Action(Enum):
        UP = 0
        DOWN = 1
        LEFT = 2
        RIGHT = 3
        FLASH = 4
        NUKE = 5
    # Define heuristic function
    # We use manhattan distance as the heuristic function
    def heuristic(goals: set, currNode: tuple) -> int:
        closestGoalDistance = float('inf')
        for goal in goals:
            goalX, goalY = goal
            manhattanDistance = abs(goalX - currNode[0]) + abs(goalY - currNode[1])
            if manhattanDistance < closestGoalDistance:
                closestGoalDistance = manhattanDistance;
        return closestGoalDistance
    
    # It is effective to use flash when total flash cost < action cost, for every action we can verify this (O(1)) operation
    def toFlash(obstacles: set, currNode: tuple, direction: int) -> bool:
        currX, currY = currNode
        while True:
            if direction == Action.UP.value: # Up
                currX -= 1
            elif direction == Action.DOWN.value: # Down
                currX += 1
            elif direction == Action.LEFT.value: # Left
                currY -= 1
            else: # Right
                currY += 1
            if (currX < 0 or currX >= rows or currY < 0 or currY >= cols or (currX, currY) in obstacles):
                return False
            if (abs(currX - currNode[0]) > 5 or abs(currY - currNode[1]) > 5):
                return True
            
    # We use nuke if the number of creeps in the manhattan region is > 50
    def toNuke(creeps: dict, currNode: tuple) -> bool:
        totalCreeps = 0
        currX, currY = currNode
        for i in range(-10, 11):
            for j in range(-10, 11):
                if abs(i) + abs(j) <= 10:
                    toCheckPos = (currX + i, currY + j)
                    if (toCheckPos in creeps and toCheckPos not in reached):
                        totalCreeps += creeps[toCheckPos]
        return totalCreeps > 50
    
    # Activate nuke effect
    def activateNuke(creeps: dict, currNode: tuple):
        for i in range(-10, 11):
            for j in range(-10, 11):
                toNuke = (currNode[0] + i, currNode[1] + j)
                if (toNuke in creeps):
                    creeps[toNuke] = 0
    start = tuple(dct['start'])
    goals = {tuple(goal) for goal in dct['goals']}
    obstacles = {tuple(obstacle) for obstacle in dct['obstacles']}
    creeps = {(creep[0], creep[1]): creep[2] for creep in dct['creeps']}
    rows = dct['rows']
    cols = dct['cols']
    flashesLeft = dct['num_flash_left']
    nukesLeft = dct['num_nuke_left']
    frontier = []
    heapq.heappush(frontier, (heuristic(goals, start), start, None, False, False))
    if start in obstacles:
        return []
    
    # Status values
    pathCost = 4
    # Flash failsafe
    beforeFlash = []
    beforeFlashReached = {}
    beforeFlashParent = {}
    # version 2
    reached = {start: (0, flashesLeft, nukesLeft)}
    parentMap = {start: (start, None, False, False)} # format: {parent: (child, direction, flash, nuke)}
    while frontier:
        cost, curr, intDir, flash, nuke = heapq.heappop(frontier)
        # print('curr:', curr)
        if curr in goals:
            path = []
            print(parentMap)
            while curr != start:
                prev, action, flash, nuke = parentMap[curr]
                if (flash):
                    path.append(Action.FLASH.value)
                else:
                    path.append(action)
                if (nuke):
                    path.append(Action.NUKE.value)
                curr = prev
            return path[::-1]
        # If we are flashing, execute it here
        # We just need to store the final position
        if (flash):
            print("*****FLASH USED IN DIR = {}*****".format(intDir))
            pathCost = 2
            initialPos = curr
            flashPos = curr
            while True:
                if intDir == Action.UP.value:
                    flashPos = (flashPos[0] - 1, flashPos[1])
                elif intDir == Action.DOWN.value:
                    flashPos = (flashPos[0] + 1, flashPos[1])
                elif intDir == Action.LEFT.value:
                    flashPos = (flashPos[0], flashPos[1] - 1)
                else:
                    flashPos = (flashPos[0], flashPos[1] + 1)
                if (flashPos[0] < 0 or flashPos[0] >= rows or flashPos[1] < 0 or flashPos[1] >= cols or flashPos in obstacles):
                    break
                reached[flashPos] = (reached[curr][0] + pathCost, reached[initialPos][1], reached[initialPos][2])
                curr = flashPos
            heapq.heappush(frontier, (reached[curr][0] + heuristic(goals, curr), curr, intDir, False, False))
            parentMap[curr] = (initialPos, intDir, False, False)
            pathCost = 4
        # If we use nuke, execute it here
        if (nuke):
            # print("*****NUKE USED*****")
            activateNuke(creeps, curr)
        # Up, Down, Left, Right
        directions = [(curr[0] - 1, curr[1]), (curr[0] + 1, curr[1]), (curr[0], curr[1] - 1), (curr[0], curr[1] + 1)]
        # Skills available: FLASH (10 MP, converts all actions to 2 MP) and NUKE (50 MP)
        for intDir, dir in enumerate(directions):
            if (0 <= dir[0] < rows and 0 <= dir[1] < cols) and dir not in obstacles:
                creepCost = creeps.get(dir, 0)
                moveCost = pathCost + creepCost
                if (dir not in reached or reached[curr][0] + moveCost < reached[dir][0]):
                    # Check if we can use flash in this direction
                    if (reached[curr][1] > 0 and toFlash(obstacles, dir, intDir)):
                        print('flashing at {}'.format(curr))
                        newCost = 10 + reached[curr][0] + moveCost # 10 for activating flash
                        reached[dir] = (newCost, reached[curr][1] - 1, reached[curr][2])
                        heapq.heappush(frontier, (newCost + heuristic(goals, dir), dir, intDir, True, False))
                        parentMap[dir] = (curr, intDir, True, False)
                        # Failsafe in the event flash was the wrong move
                        beforeFlash.append((newCost - 10 + heuristic(goals, dir), dir, intDir, False, False))
                        beforeFlashReached = reached.copy()
                        beforeFlashReached[dir] = (newCost, reached[curr][1], reached[curr][2])
                        beforeFlashParent = parentMap.copy()
                        beforeFlashParent[dir] = (curr, intDir, False, False)
                        continue
                    # Check if we can use nuke at this state
                    if (reached[curr][2] > 0 and toNuke(creeps, dir)):
                        newCost = 50 + reached[curr][0] + moveCost # 50 for activating nuke
                        reached[dir] = (newCost, reached[curr][1], reached[curr][2] - 1)
                        heapq.heappush(frontier, (newCost + heuristic(goals, dir), dir, intDir, False, True))
                        parentMap[dir] = (curr, intDir, False, True)
                        continue
                    newCost = reached[curr][0] + moveCost
                    heapq.heappush(frontier, (newCost + heuristic(goals, dir), dir, intDir, False, False))
                    reached[dir] = (reached[curr][0] + moveCost, reached[curr][1], reached[curr][2])
                    parentMap[dir] = (curr, intDir, False, False)
        # In the event flashing was the wrong move
        if not frontier and beforeFlash:
            print("try without flash:", beforeFlash)
            reached = beforeFlashReached
            parentMap = beforeFlashParent
            print(reached)
            heapq.heappush(frontier, beforeFlash.pop())
    return []
parser = argparse.ArgumentParser(description="Run DFS with a JSON file input.")
parser.add_argument("json_file", type=str, help="Path to the JSON file")
args = parser.parse_args()
with open(args.json_file, "r") as file:
    data = json.load(file)
print('start:', data['start'], 'goals:', data['goals'])
print(search(data))