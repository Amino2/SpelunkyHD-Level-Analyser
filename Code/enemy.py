import math

solidTiles = ['1','#']
#This will monitor what step in the path the player was on, when the enemies aggro's onto them.
encounterSteps = []

class Enemy:
    def __init__(self, position, damage, health, speed, aggroRange, enemyCoverage, pathingComplexityScore):
        self.position = position
        self.damage = damage
        self.health = health
        self.speed = speed
        self.aggroRange = aggroRange
        self.enemyCoverage = enemyCoverage
        self.pathingComplexityScore = pathingComplexityScore
        self.playerPos = None  #Will be assigned later when the players position for the instance is found
        self.difficulty_score = None  #Computed later

    def __repr__(self):
        return f"{self.__class__.__name__}(position={self.position})"

    def enemyWeight(self):
        weight = self.health + self.damage + self.speed + (0.1 * self.enemyCoverage) + self.pathingComplexityScore
        return weight



class Bat(Enemy):
    def __init__(self, position, damage=1, health=1, speed=2, aggroRange=None, enemyCoverage=49, pathingComplexityScore=2):
        super().__init__(position, damage, health, speed, aggroRange, enemyCoverage, pathingComplexityScore)

    def is_in_range(self, path):
        i=0
        enemyX, enemyY = self.position
        for playerX, playerY in path:
            i+=1
            xDistance = abs(playerX - enemyX)
            yDistance = playerY - enemyY

            if (
                (1 <= yDistance <= 3 and xDistance <= 5) or
                (yDistance == 4 and xDistance <= 4) or
                (yDistance == 5 and xDistance <= 3)
            ):
                encounterSteps.append(i)
                return (playerX, playerY)
        return None

    def compute_difficulty_score(self, enemyGrid):
        #5tiles is the max tile range for the bat
        maxBatTime = 5 / self.speed  
        minBatTime = 1 / self.speed
        batTimePath = aStarSearchBat(enemyGrid, self.position, self.playerPos, 1)
        totalTiles = len(batTimePath)
        timeToPlayer = totalTiles / self.speed
        timeScore = (maxBatTime - timeToPlayer) / (maxBatTime - minBatTime)

        #We add the 0 parameter so that it does not travel diagonally, so we can get as much obstacle data as possible
        batObstaclePath = aStarSearchBat(enemyGrid, self.position, self.playerPos, 0)
        maxObstacles = len(batObstaclePath)
        obstacleCount = 0
        for coord in batObstaclePath:
            if enemyGrid[coord] in solidTiles:
                obstacleCount +=1
        obstacleScore = 1 - (obstacleCount / maxObstacles)
        difficultyScore = (timeScore + obstacleScore) / 2
        difficultyScore = max(0.2, difficultyScore)
        difficultyScore = round(difficultyScore, 2)
        self.difficulty_score = difficultyScore
        return difficultyScore

class Caveman(Enemy):
    def __init__(self, position, damage=1, health=3, speed=4, aggroRange=5, enemyCoverage=10, pathingComplexityScore=1):
        super().__init__(position, damage, health, speed, aggroRange, enemyCoverage, pathingComplexityScore)

    def is_in_range(self, path):
        i=0
        enemyX, enemyY = self.position
        for playerX, playerY in path:
            i+=1
            x_Distance = abs(playerX - enemyX)
            #The cavemans range is 5 or less, so long as the player is on the same elevation as the enemy
            if enemyY == playerY and 1<= x_Distance <=5:
                encounterSteps.append(i)
                return (playerX, playerY)
        return None

    def compute_difficulty_score(self, enemyGrid):
        enemyX, enemyY = self.position
        playerX, playerY = self.playerPos
        maxCaveManTime = self.aggroRange / self.speed
        minCaveManTime = 1 / self.speed
        totalTiles = abs(playerX - enemyX)
        timeToPlayer = totalTiles / self.speed
        timeScore = (maxCaveManTime - timeToPlayer) / (maxCaveManTime - minCaveManTime)
        timeScore = max(0.2, timeScore)

        #This code checks if the caveman can reach the player
        cavemanBlocked = False
        #These 2 variables are needed, because the caveman can aggro onto the player from 2 different directions, left and right, so we need to account for both cases
        loopStart = min(enemyX, playerX)
        loopEnd = max(enemyX, playerX)
        for x in range(loopStart, loopEnd+1):
            #Check if below has some gap to stop the enemy reaching the player
            #The first check is for gaps under the caveman, the second check is for tiles blocking the caveman
            if enemyGrid[x, enemyY +1] not in solidTiles or enemyGrid[x, enemyY -1] in solidTiles: 
                cavemanBlocked = True
                break
        if cavemanBlocked:
            #Make sure difficulty does not go below 0.2
            difficultyScore = max(timeScore * 0.5, 0.2)
        else:
            #Make sure difficulty does not exceed 1
            difficultyScore= min(timeScore * 1.2, 1)
        difficultyScore = round(difficultyScore, 2)
        self.difficulty_score = difficultyScore
        return difficultyScore
    
class Arachnid(Enemy):
    def __init__(self, position, damage=1, health=1, speed=10, aggroRange=6, enemyCoverage=6, pathingComplexityScore=3):
        super().__init__(position, damage, health, speed, aggroRange, enemyCoverage, pathingComplexityScore)

    def is_in_range(self, path):
        i=0
        enemyX, enemyY = self.position
        for playerX, playerY in path:
            i+=1
            y_Distance = playerY - enemyY
            if enemyX == playerX and 1<= y_Distance <=6: #The spiders range is 6 tiles or less below it
                encounterSteps.append(i)
                return (playerX, playerY)
        return None

    def compute_difficulty_score(self, enemyGrid):
        enemyX, enemyY = self.position
        playerX, playerY = self.playerPos
        maxSpiderTime = self.aggroRange / self.speed
        minSpiderTime = 1 / self.speed
        totalTiles = playerY - enemyY
        timeToPlayer = totalTiles / self.speed
        timeScore = (maxSpiderTime - timeToPlayer) / (maxSpiderTime - minSpiderTime)
        timeScore = max(0.2, timeScore)

        #This code checks if the caveman can reach the player
        spiderBlocked = False
        for y in range(enemyY, playerY+1):
            #Check if below has some gap to stop the enemy reaching the player
            if enemyGrid[enemyX, y] in solidTiles:
                spiderBlocked = True
                break
        if spiderBlocked:
            #Make sure difficulty does not go below 0.2
            difficultyScore = max(timeScore * 0.8, 0.2)
        else:
            #Make sure difficulty does not exceed 1
            difficultyScore= min(timeScore * 1.2, 1)

        difficultyScore = round(difficultyScore, 2)
        self.difficulty_score = difficultyScore
        return difficultyScore

class Snake(Enemy):
    def __init__(self, position, grid, snakePlatform = None, damage=1, health=1, speed=1.5, aggroRange=0, enemyCoverage=0, pathingComplexityScore=1):
        super().__init__(position, damage, health, speed, aggroRange, enemyCoverage, pathingComplexityScore)
        self.grid = grid

    def is_in_range(self, path):
        i=0

        #Define the snake's platform:
        seedTile = self.position[0]
        yPos = self.position[1]
        snakePlatform = []
        #Check the left side first 
        xPos = seedTile
        snakePlatform.append((xPos,yPos))
        while True:
            xPos -= 1
            #We do yPos+1 because the solid tile platform is below the snake's position
            if self.grid[xPos, yPos+1] in solidTiles and self.grid[xPos, yPos] not in solidTiles:
                #snakePlatform may be better named as "snakePath", but this is debatable
                snakePlatform.append((xPos,yPos))
            else:
                break
        #Then the right side
        xPos = seedTile
        while True:
            xPos += 1
            #We do yPos+1 because the solid tile platform is below the snake's position
            if self.grid[xPos, yPos+1] in solidTiles and self.grid[xPos, yPos] not in solidTiles:
                #snakePlatform may be better named as "snakePath", but this is debatable
                snakePlatform.append((xPos,yPos))
            else:
                break
        
        snakePlatform.sort()
        #snakePlatform is specific to the snake-type enemies because the platform is needed to compute difficulty
        self.snakePlatform = snakePlatform
        for playerX, playerY in path:
            i+=1
            #If the player goes onto the snakes platform (essentially the snakes path coordinates)
            if (playerX, playerY) in snakePlatform:
                encounterSteps.append(i)
                return (playerX, playerY)
        return None

    def compute_difficulty_score(self, enemyGrid):
        #Snake's difficulty is simply based on platform length
        platformLength = len(self.snakePlatform)
        if platformLength <=1:
            difficultyScore = 0.2
        elif 1< platformLength <=3:
            difficultyScore = 1
        elif 3< platformLength <=5:
            difficultyScore = 0.8
        elif 5< platformLength <=8:
            difficultyScore = 0.4
        else:
            difficultyScore = 0.2
        return difficultyScore

class Cobra(Enemy):
    def __init__(self, position, grid, shootingPoints = None, maxProjFall = None, totalTileCoverage = None, damage=1, health=1, speed=1.5, aggroRange=0, enemyCoverage=0, pathingComplexityScore=1):
        super().__init__(position, damage, health, speed, aggroRange, enemyCoverage, pathingComplexityScore)
        self.grid = grid

    def is_in_range(self, path):
        #Same process as the normal snake, find out the snake's platform
        seedTile = self.position[0]
        yPos = self.position[1]
        snakePlatform = []
        #Check the left side first 
        xPos = seedTile
        snakePlatform.append((xPos,yPos))
        while True:
            xPos -= 1
            if self.grid[xPos, yPos+1] in solidTiles and self.grid[xPos, yPos] not in solidTiles:
                snakePlatform.append((xPos,yPos))
            else:
                break
        #Then the right side
        xPos = seedTile
        while True:
            xPos += 1
            if self.grid[xPos, yPos+1] in solidTiles and self.grid[xPos, yPos] not in solidTiles:
                snakePlatform.append((xPos,yPos))
            else:
                break

        #Now, we calculate where the snake will be spitting from, including direction.
        spitCooldown = 3  # Cobra spits every 3 tiles
        shootingPoints = []
        x, y = self.position  # Initialize cobra's starting position

        #Platform boundaries
        platformStartX = snakePlatform[0][0]
        platformEndX = snakePlatform[-1][0]

        #Initialize direction and cycle count
        direction = 1  #1 for rightwards, -1 for leftwards, this models the direction the snake is facing, and thus spitting direction
        distanceTally = 0
        cyclesCompleted = 0
        #Total number of cycles we are checking, 3 cycles of the snake going from leftest point to the rightest point
        #This is to make sure we got all spitting points, as they may differ even over multiple cycles
        maxCycles = 3  

        while cyclesCompleted < maxCycles:
            #Move the cobra and track the distance
            if distanceTally % spitCooldown == 0 and distanceTally != 0:
                #Cobra shoots projectile
                shootingPoints.append((x, y, direction))
            
            #Cobra moves one tile
            x += direction
            distanceTally += 1
            
            #Check if cobra has reached the edge
            if x == platformEndX or x == platformStartX:
                #Add shooting point at the edge
                shootingPoints.append((x, y, direction))
                
                #Reverse direction
                direction *= -1
                #Reset distance tally, as snake has just spat
                distanceTally = 0
                #Increment the cycle count if it has completed a full cycle (touching both edges)
                cyclesCompleted += 1


        self.shootingPoints = shootingPoints
        hitsPlayerPath, maxFallDistance, totalTileCoverage = cobraProjectileTrajectory (shootingPoints, self.grid, path)
        self.maxProjFall = maxFallDistance
        self.totalTileCoverage = totalTileCoverage
        if hitsPlayerPath:
            #This should pass the if check in checkEncounters
            return(hitsPlayerPath)
        else:
            return None

    def compute_difficulty_score(self, enemyGrid):
        #We start the difficulty calculation by getting the speed at which the projectile is hitting the ground, giving velocityScore
        #The gravity has been measured over multiple clips as acceleration of 31 tiles/s^2
        projectileGravity = 31
        
        yVelocity = math.sqrt(2 * projectileGravity * self.maxProjFall)
        maxVelocity = math.sqrt(2 * projectileGravity * 4)
        velocityScore = yVelocity/maxVelocity
        velocityScore = min(1, velocityScore)
        
        #coverageScore refers to how many unique tiles the cobra covers with the projectile shot
        #10 unique tiles is a placeholder, I believe it is a good placeholder for a very problematic cobra for the player
        coverageScore = self.totalTileCoverage / 10
        coverageScore = min(1, coverageScore)

        #An average is taken
        difficultyScore = (coverageScore + velocityScore) / 2
        difficultyScore = round(difficultyScore, 2)
        difficultyScore = max(0.2,difficultyScore)
        return difficultyScore

def cobraProjectileTrajectory (coordinates, grid, path):
    maxFall = 0
    #Used to map out the unique coordinates which the projectile covers
    projectileCoordinates = []
    hitsPlayerPath = False
    
    #The sequence the projectile takes, measured by hand from the game
    trajectory_sequence = [(1, 0), (1, 0), (1, 0), (1, 1), (1, 0), (0, 1), (1, 0), (0, 1), (1, 0), (0, 1), (0, 1), (1, 0), (0, 1), (1, 1), (0, 1), (1, 0), (0, 1)]
    
    #This loop checks for if any of the cobras shots hit the players taken path
    #It also finds the max distance travelled for a projectile from the cobra
    for coordinate in coordinates:
        x, y, direction = coordinate

        startY = y
        #Process the trajectory
        for dx, dy in trajectory_sequence:
            x += dx * direction
            y += dy #Not affected by direction because the projectile can only go down

            tileAtGrid = grid[x,y]
            if (x,y) in path:

                maxFall = max((y - startY), maxFall)
                hitsPlayerPath = (x,y)
                if (x,y) not in projectileCoordinates:
                    projectileCoordinates.append((x,y))
                #We dont break the loop here because we need to find the max speed of the projectile
            #Check if the grid_value is in solid_tiles
            elif tileAtGrid in solidTiles:
                break
            else:
                if (x,y) not in projectileCoordinates:
                    projectileCoordinates.append((x,y))

    totalTileCoverage = len(projectileCoordinates)
    return (hitsPlayerPath, maxFall, totalTileCoverage)

def checkEnemies(path, enemyGrid):
    #All enemies present in the level
    allEnemies = []
    #Enemies which aggro onto the Spelunker or get in the way
    activeEnemies = []

    enemyPotentialScores = []
    enemyWeightedScores = []

    for (x, y), char in enemyGrid.items():
        if char == "B":
            allEnemies.append(Bat((x, y)))
        elif char == "C":
            allEnemies.append(Caveman((x, y)))
        elif char == "A":
            #A for arachnid
            allEnemies.append(Arachnid((x, y)))
        elif char == "S":
            allEnemies.append(Snake((x, y), enemyGrid))
        elif char == "P":
            #P for projectile
            allEnemies.append(Cobra((x, y), enemyGrid))

    #Checking if any enemies are in range, and then calculating their difficulty
    for enemy in allEnemies:
        #Player position will be the first coordinate in path which is in range of that enemy
        player_position = enemy.is_in_range(path)
        if player_position:
            activeEnemies.append(enemy)
            enemy.playerPos = player_position
            enemy.difficulty_score = enemy.compute_difficulty_score(enemyGrid)
            enemyPotentialScores.append(enemy.difficulty_score)

            weight = enemy.enemyWeight()
            #print(f"{type(enemy).__name__} 's Weight score is: ", weight)
            weightedScore = weight * enemy.difficulty_score
            weightedScore = round(weightedScore, 2)
            enemyWeightedScores.append(weightedScore)
            
            activeEnemyCount = len(activeEnemies)
            allEnemyCount = len(allEnemies)

            #print(f"{type(enemy).__name__} at {enemy.position} found the player at {enemy.playerPos}, The difficulty score was: {enemy.difficulty_score}")
            
    return encounterSteps, enemyPotentialScores, enemyWeightedScores, activeEnemyCount, allEnemyCount


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(pos, diagonal):
    x, y = pos
    #Bat can move to any adjacent tile
    neighbors = [(x, y+1), (x+1, y), (x, y-1), (x-1, y)]
    if diagonal:
        neighbors.extend([
            (x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)
        ])
    return neighbors

def aStarSearchBat(grid, start, goal, diagonal):
    openSet = [start]  #Initialize open set with start position
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    
    while openSet:
        #Find the node in open_set with the lowest fscore
        current = min(openSet, key=lambda o: fscore.get(o, float('inf')))
        openSet.remove(current)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            #path.append(start)
            path.reverse()
            return path
        
        #Explore neighbors
        for neighbor in get_neighbors(current, diagonal):
            x_max = max(coord[0] for coord in grid)
            y_max = max(coord[1] for coord in grid)
            
            if 0 <= neighbor[0] < x_max and 0 <= neighbor[1] < y_max:
                #Update scores if the path is better
                tentative_g_score = gscore[current] + 1
                
                if neighbor not in gscore or tentative_g_score < gscore[neighbor]:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    
                    if neighbor not in openSet:
                        openSet.append(neighbor)
    
    #Return False if no path has been found
    return False