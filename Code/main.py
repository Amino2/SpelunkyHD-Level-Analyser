from collections import deque
from enemy import checkEnemies
from traps import checkTraps
from layout import fallCheck
import time
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import statistics

#This is used to define jumps, where they will later be stored in a list
class JumpPath:
    def __init__(self, start, end, path_coordinates, danger_level):
        self.start = start
        self.end = end
        self.path_coordinates = path_coordinates
        self.danger_level = danger_level

    def __str__(self):
        return f"JumpPath from {self.start} to {self.end} with danger level {self.danger_level}"

#Global variables:

#This stores the items and places the player needs to path to to collect, FIFO list
placesOfInterest = []
#This stores any locations already found or ones which cannot be reached
seenOrUnobtainable = []

#Used by the exploration mode, where we check if the epxloration points have already been seen, to avoid going over the same location twice
seenCoordinates = []

#This stores the currentFloor the player is on
currentFloor = 0

#Stores the path taken by the player
logPath = []

#Here are the collectables the player will want to collect
collectables = ['C']

#Tiles the player can traverse THROUGH
traversableTiles = [".", ",","9","8","E","C","L","s"]

#Tiles the player can walk ON / are solid. "1" is the solid rock tile, "a" is the arrow trap
solidTiles = ['1','a']

#For testing
totalChecks = 0

def mapTraversableNodes(gridDictionary):
    #First loop adds the simplest traversable characters, where there is a block with a gap above it.
    for (x, y), char in gridDictionary.items():
        if char != "#":
            belowChar = gridDictionary.get((x, y + 1))
            if char == " " and belowChar in solidTiles:
                gridDictionary[(x, y)] = '.'

    #Second loop adds "E"s on each ledge, which are used later to map the vertical drops, later replaced by "."
    for (x, y), char in gridDictionary.items():
        if char != "#":
            left_char = gridDictionary.get((x - 1, y))
            right_char = gridDictionary.get((x + 1, y))
            
            under_left_char = gridDictionary.get((x - 1, y+1))
            under_right_char = gridDictionary.get((x + 1, y+1))
            #Here we check if there is a ledge, which is an empty space next to an edge "."
            if char == " ":
                if left_char == "." or right_char == ".":
                    gridDictionary[(x, y)] = 'E'
                # or next to a Ladder which is on top of a platform
                if (left_char == "L" or right_char == "L") and (under_left_char == "P" or under_right_char == "P"):
                    gridDictionary[(x, y)] = 'E'
    
    #Third loop adds verticality to the grid, "," denotes falling only, "." denotes a jumpable (up or down) distance
    for (x, y), char in gridDictionary.items():
        if char != "#":
            #We wabt to measure the falls which come under any "E" (edges)
            if char == "E":
                current_y = y + 1  # Start checking from the row below the 'L'
                distance = 1 # This measures the height of the fall, a height of 1 means the player can jump to the ledge
                while True:
                    # Get the character at the current coordinate
                    current_char = gridDictionary[(x, current_y)]
                    if current_char == ' ':
                        #Checks if the distance is small enough for a ledge grab, and or a jump up by the spelunker (2 in 1 essentially)
                        if distance == 1:
                            gridDictionary[(x, current_y)] = '.'
                            distance += 1
                        else:
                            # The ',' denotes falling (down only) for any future pathing algorithm used
                            gridDictionary[(x, current_y)] = ','
                    #Makes sure the loop stops if the fall hits something, and also doesnt overwrite any "."s
                    elif current_char in {'.', 'E', '#', 's'} or current_char in solidTiles:
                        break
                    # Move to the next row
                    current_y += 1
    
    return gridDictionary


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(pos, grid):
    x, y = pos
    if grid.get((x, y)) in traversableTiles:
        return [(x, y+1), (x+1, y), (x, y-1), (x-1, y)]
    #Checks for the down only character ','
    elif grid.get((x, y)) == ",":
        return [(x, y+1)]
    return []

def a_star_search(grid, start, goal):
    closeSet = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    openSet = [start]

    while openSet:
        #Find the node in open_set with the lowest fscore
        current = min(openSet, key=lambda o: fscore.get(o, float('inf')))
        openSet.remove(current)

        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            data.append(start)
            #Reverse the path so it is in the right order to use later
            data.reverse()
            return data

        closeSet.add(current)
        for neighbor in get_neighbors(current, grid):
            tentative_g_score = gscore[current] + 1
            x_max = max(coord[0] for coord in grid)
            y_max = max(coord[1] for coord in grid)
            if 0 <= neighbor[0] < x_max:
                if 0 <= neighbor[1] < y_max:
                    #This is the list of characters which the player can traverse, must represent some sort of tile the player can walk through
                    if grid.get(neighbor) not in traversableTiles:
                        continue
                else:
                    continue
            else:
                continue

            if neighbor in closeSet and tentative_g_score >= gscore.get(neighbor, 0):
                continue

            if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in openSet:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                if neighbor not in openSet:
                    openSet.append(neighbor)
    
    #Returns false if no path has been found
    return False

def find_extremes(grid, start):
    yBounds = getYBounds(start[1])
    
    queue = deque([start])
    visitedNodes = set()
    visitedNodes.add(start)

    reachable_leftmost = start
    reachable_rightmost = start

    while queue:
        x, y = queue.popleft()
        
        #Check the neighbors: up, down, left, right
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in grid and grid[(nx, ny)] in traversableTiles and (nx, ny) not in visitedNodes:
                if yBounds[0] <= ny <= yBounds[1]:  #Check if within floor bounds
                    queue.append((nx, ny))
                    visitedNodes.add((nx, ny))
                    
                    #Check if the node is reachable by the player and update if needed
                    if nx < reachable_leftmost[0] and a_star_search(grid, start, (nx, ny)):
                        reachable_leftmost = (nx, ny)
                    if nx > reachable_rightmost[0] and a_star_search(grid, start, (nx, ny)):
                        reachable_rightmost = (nx, ny)

    #In case no nodes were found, or the coordinate has already been explored, the code should return None
    if reachable_leftmost == start or reachable_leftmost in seenCoordinates:
        #print("Leftmost was not reachable or it has already been seen,, it was: ", reachable_leftmost)
        reachable_leftmost = None
    if reachable_rightmost == start or reachable_rightmost in seenCoordinates:
        #print("Rightmost was not reachable or it has already been seen, it was: ", reachable_rightmost)
        reachable_rightmost = None
    
    if reachable_leftmost is None and reachable_rightmost is None:
        return None

    return reachable_leftmost, reachable_rightmost

#This function goes through the grid and finds potential jumps the player can do, and then maps out the danger level for each jump
#The hope is that the A* pathing algorithm can recognise when a jump has taken place, and that jump's danger level should be recorded each time it is used
def jumpMapper(grid):
        #We create this clone to seperate from the original 
        initialJumpingGrid = grid.copy()
        jumpList = []
        for (x, y), char in grid.items():
            #jump = JumpPath(startCoord, endCoord, intermediatePath, dangerLevel)
            #jumpList.append(jump)
            if char == 'E':
                #Initialise the start coordinate of the jump, which we would say begins at the edge 'E'
                startCoord = (x,y)
                intermediatePath = []
                #for
                #We need to scan above and below, because jumps can be to a block above, below, or on the same y value as the start block
                #We dont want to scan too far down as that isnt a valid jump due to fall damage, and not too high up as that isnt a possible jump
                current_x = x
                while True:
                    current_x += 1
                    if current_x:
                        #temp
                        break

def checkLevel(y):
    level = None
    #Calculate the current level from 1-4 the player is on
    if 3 <= y <= 10:
        level = 1
    elif 11<= y <= 18:
        level = 2
    elif 19<= y <= 26:
        level = 3
    elif 27<= y <= 37:
        level = 4
    else:
        level = (None)
    
    return level

def getYBounds(y):
    if 3 <= y <= 10:
        bounds = (3,10)
    elif 11<= y <=18:
        bounds = (11,18)
    elif 19<= y <= 26:
        bounds = (19,26)
    elif 27<= y <=37:
        bounds = (27,34)
    else:
        bounds = (None,None)
    
    return bounds

def newFloorCheck(y):
    
    #Set to 0 before the level starts
    global currentFloor
    if checkLevel(y) != currentFloor:
        currentFloor += 1
        print("New floor reached! Now at floor: ", currentFloor)
        return True
    else:
        return False

def checkSurroundings(grid, currentPos):
    global totalChecks
    totalChecks = totalChecks +1
    # The camera in Spelunky can see 5 tiles above and below,
    # and 10 tiles to the left and right from the player's position.
    x, y = currentPos
    playerLevel = checkLevel(y)

    # Calculate the initial camera bounds
    top_Y = y - 5
    bottom_Y = y + 5
    left_X = x - 10
    right_X = x + 10

    # The level dimensions
    level_width = 46
    level_height = 38

    # Adjust the camera bounds if they exceed the level boundaries
    if left_X < 0:
        excessX = abs(left_X)
        left_X = 0
        right_X += excessX

    if right_X >= level_width:
        excessX = right_X - level_width + 1
        right_X = level_width - 1
        left_X -= excessX

    if top_Y < 0:
        excessY = abs(top_Y)
        top_Y = 0
        bottom_Y += excessY

    if bottom_Y >= level_height:
        excessY = bottom_Y - level_height + 1
        bottom_Y = level_height - 1
        top_Y -= excessY
    count = 0

    for x in range(left_X, right_X + 1):
        for y in range(top_Y, bottom_Y + 1):
            count+=1
            key = (x, y)
            #Adds each coordinate to the seenCoordinates list used in other functions
            if key not in seenCoordinates:
                seenCoordinates.append(key)
            #Need to check bc it may be out of bounds
            #if key in grid:
            value = grid[key]

            if value in collectables and (key, value) not in seenOrUnobtainable:
                itemLevel = checkLevel(y)
                #This check is needed so we ignore items on levels that the player isnt on
                if itemLevel == playerLevel:
                    #Checks if this specific item has already been "seen"
                    pathCheck = a_star_search(grid, currentPos, key)
                    if pathCheck:
                        print("New item added")
                        placesOfInterest.append((key, value))
                        seenOrUnobtainable.append((key, value))
                    else:
                        print("unobtainable item at: ", key, value)
                        seenOrUnobtainable.append((key, value))
    return

#This function loops through the grid to find the start and end points of each level
def findStartEnd(grid):
    start = None
    end = None
    for coordinate, value in grid.items():
        if value == '9':
            #print(coordinate, value)
            start = coordinate
        elif value == '8':
            #print(coordinate, value)
            end = coordinate
        #End search early if they have already been found
        if (start is not None) and (end is not None):
            break

    return start, end

def createGrid(fileName):
    with open(fileName) as file:
        level = [line.rstrip() for line in file]

    #Convert level structure to a dictionary
    #The keys are the coordinates, and the value is the ascii char
    grid_dict = {}
    for y, row in enumerate(level):
        for x, char in enumerate(row):
            grid_dict[(x, y)] = char

    #Call the function which creates all the reachable nodes for the player and alters the grid dictionary
    traversableGrid = mapTraversableNodes(grid_dict)
    return traversableGrid

def printGrid(grid):
    counter = 0
    for (x, y), char in grid.items():
        print(char, end='')
        counter += 1
        if counter % 46 == 0:
            print()  #new line after 46 characters (one row)
    print()

def main():
    startTime = time.time()
    #Create grid
    traversableGrid = createGrid('Data/UserStudy/easierStructure.txt')
    print("\n")
    enemyGrid = createGrid('Data/UserStudy/easierEnemyGrid.txt')

    #jumpingGrid = jumpMapper(traversableGrid)

    #This function gets the locations of the start (to be the first position) and end coordinates
    levelStart, levelEnd = findStartEnd(traversableGrid)

    explorationPoints = find_extremes(traversableGrid, levelStart)
    Mode = None
    levelFinished = False
    currentPosition = levelStart

    while not levelFinished:
        checkSurroundings(traversableGrid,currentPosition)
        #Set the mode, collect mode is prioritised, the exploration then progress
        if placesOfInterest:
            print("Starting Collect mode")
            Mode = "Collect"
        elif explorationPoints:
            print("Starting Explore mode")
            Mode = "Explore"
        else:
            print("Starting Progress mode")
            Mode = "Progress"


        if Mode == "Collect":
            currentGoal = placesOfInterest[0][0]
            path = a_star_search(traversableGrid, currentPosition, currentGoal)
            for coordinate in path:
                if newFloorCheck(coordinate[1]):
                    explorationPoints = find_extremes(traversableGrid, coordinate)
                checkSurroundings(traversableGrid,coordinate)
                logPath.append(coordinate)
            currentPosition = currentGoal
            print("collected item ", placesOfInterest[0][1]," at ", placesOfInterest[0][0])
            placesOfInterest.pop(0)

        elif Mode == "Explore":
            leftmostPoint, rightmostPoint = explorationPoints
            print("Current location: ", currentPosition, "Currently exploring these points: ", leftmostPoint, rightmostPoint)
            progress_interrupted = False
            if leftmostPoint is not None:
                path = a_star_search(traversableGrid, currentPosition, leftmostPoint)
                for coordinate in path:
                    checkSurroundings(traversableGrid,coordinate)
                    logPath.append(coordinate)
                    if placesOfInterest:
                        print("Exploration paused, item found!")
                        currentPosition = coordinate
                        progress_interrupted = True
                        break
                
                if not progress_interrupted:
                    #print("Teleporting to Left exploration point: ", leftmostPoint)
                    currentPosition = leftmostPoint
            
            if rightmostPoint is not None:
                path = a_star_search(traversableGrid, currentPosition, rightmostPoint)
                for coordinate in path:
                    checkSurroundings(traversableGrid,coordinate)
                    logPath.append(coordinate)
                    if placesOfInterest:
                        print("Exploration paused, item found!")
                        currentPosition = coordinate
                        progress_interrupted = True
                        break

                if not progress_interrupted:
                    #print("Teleporting to Left exploration point: ", rightmostPoint)
                    currentPosition = rightmostPoint
                
            if not progress_interrupted:
                explorationPoints = None
            

        elif Mode == "Progress":
            currentGoal = levelEnd
            if currentGoal == currentPosition:
                #This is the case because if the mode is set to "Progress" then they have already done everything on that
                levelFinished = True
            else:
                #We load the entire path before checking each position, if anything is found or if a new floor is reached, then the mode must be changed / rechecked
                path = a_star_search(traversableGrid, currentPosition, currentGoal)
                #print("CurrentPos: ", currentPosition, "Goal: ", currentGoal)
                #print("Starting progression path")
                progress_interrupted = False
                for coordinate in path:
                    print("Currently progressing, current coordinate: ", coordinate)
                    checkSurroundings(traversableGrid,coordinate)
                    logPath.append(coordinate)
                    if placesOfInterest:
                        #print("Progression paused, item found!")
                        currentPosition = coordinate
                        break
                    if newFloorCheck(coordinate[1]):
                        explorationPoints = find_extremes(traversableGrid, coordinate)
                        currentPosition = coordinate
                        progress_interrupted = True
                        break
                #print("Teleporting to end of progression")
                if not progress_interrupted:
                    currentPosition = path[-1]
    if levelFinished:
        print("Level finished succesfully")
    else:
        print("Level was not completed")
    
    #print("Final path taken:")
    #print(logPath)

    for (x, y), char in traversableGrid.items():
        if (x, y) in logPath:
            if char == ",":
                traversableGrid[(x, y)] = "v"
            elif char != "v": #Just so it doesnt overwrite any old v's
                traversableGrid[(x, y)] = "~"
    
    printGrid(traversableGrid)

    enemyEncounterSteps, enemyPotentialScores, enemyWeightedScores, activeEnemyCount, allEnemyCount = checkEnemies(logPath, enemyGrid)
    trapEncounterSteps, trapPotentialScores, trapWeightedScores, activeTrapCount, allTrapcount = checkTraps(logPath,enemyGrid)
    print("Enemy stats:")
    print(activeEnemyCount)
    print(allEnemyCount)
    
    print("Trap stats: ")
    print(activeTrapCount)
    print(allTrapcount)
    fallDistances = fallCheck(traversableGrid)

    avgEnemyPotential = round(statistics.mean(enemyPotentialScores)*100,2)
    avgEnemyWeight = round(statistics.mean(enemyWeightedScores),2)
    totalEnemyWeight = round(np.sum(enemyWeightedScores), 2)
    activeEnemyAvg = round((activeEnemyCount/allEnemyCount)*100,2)
    print("*** ENEMY STATS ***")
    print("Average enemy potential: ", avgEnemyPotential, "%")
    print("Average enemy weightScore: ", avgEnemyWeight)
    print("Total enemy weight Score: ", totalEnemyWeight)
    print("Percentage of active enemies / all enemies: ",activeEnemyAvg , "%")
    print("Total active enemies: ", activeEnemyCount)


    avgTrapPotential = round(statistics.mean(trapPotentialScores)*100,2)
    avgTrapWeight = round(statistics.mean(trapWeightedScores),2)
    totalTrapWeight = round(np.sum(trapWeightedScores), 2)
    activeTrapAvg = round((activeTrapCount/activeTrapCount)*100,2)
    print("\n*** TRAP STATS ***")
    print("Average trap potential: ", avgTrapPotential, "%")
    print("Average trap weightScore: ", avgTrapWeight)
    print("Total trap weight Score: ", totalTrapWeight)
    print("Percentage of active traps / all traps: ",activeTrapAvg , "%")
    print("Total active traps: ", activeTrapCount)
    
    combined_array = trapEncounterSteps + enemyEncounterSteps
    combined_array.sort()

    length = len(combined_array)
    totalEvents = 0
    eventsArray = []

    #start eventsArray with all 0s
    max_value = max(combined_array) if combined_array else 0
    eventsArray = [0] * (max_value + 1)

    #each index is counted
    for index in combined_array:
        eventsArray[index] += 1

    #add up the counts
    for i in range(1, len(eventsArray)):
        eventsArray[i] += eventsArray[i - 1]
        
    ypoints = np.array(eventsArray)

    endTime = time.time()
    totalExecutionTime = round((endTime - startTime), 2)
    print("Runtime: ",totalExecutionTime, "s")
    plt.plot(ypoints)
    plt.xlabel('Path steps taken')
    plt.ylabel('Obstacle encounters')
    plt.show()

if __name__ == '__main__':
    main()