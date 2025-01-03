obstacleTiles = ['a','P','C','S','A','B']
solidTiles = ['1','#']
encounterSteps = []

class spikes:
    #The spikes have "instakill" levels of damage to compensate for its lack of mobility
    def __init__(self, position, damage = 99): 
        self.position = position
        self.damage = damage

    def trapWeight(self):
        #We reduce the stationary trap's damage because it is always going to be high due to its nature
        weight = 0.2 * self.damage
        weight = round(weight, 2)
        return weight

    def __repr__(self):
        return f"{self.__class__.__name__}(position={self.position})"

    def is_in_range(self, path):
        i=0
        trapX, trapY = self.position
        for playerX, playerY in path:
            i+=1
            x_Distance = abs(playerX - trapX)
            y_Distance = abs(playerY - trapY)
            #Makes sure the player is above or on the same level as the spikes, and checks they're within range
            if playerY <= trapY and x_Distance <=6 and y_Distance <=5:
                encounterSteps.append(i)
                return (playerX, playerY)
        #The spikes only hurt the player when they are below the player
        
        return None

    def compute_difficulty_score(self, enemyGrid):
        xStart, yStart = self.position
        obstacles = 0
        for dx in range(-6, 6+1):
            for dy in range (-6, 1): #We dont want to check below the y of the spike
                x = xStart + dx
                y = yStart + dy
                #We use .get to avoid key errors
                tile = enemyGrid.get((x, y))
                if tile in obstacleTiles:
                    obstacles += 1

        if obstacles >= 5:
            difficultyScore = 1
        elif 3<= obstacles <=4:
            difficultyScore = 0.8
        elif 1<= obstacles <=2:
            difficultyScore = 0.5
        elif obstacles == 0:
            difficultyScore = 0.2
        else:
            difficultyScore = 0.2

        return difficultyScore
    


class ArrowTrap:
    def __init__(self, position, grid, aggroRange=6, facingMultiplier = None, playerPos = None, speed = 30, damage = 2):
        self.position = position
        self.grid = grid
        self.aggroRange = aggroRange
        self.facingMultiplier = facingMultiplier
        self.playerPos = playerPos
        self.speed = speed
        self.damage = damage

    def __repr__(self):
        return f"{self.__class__.__name__}(position={self.position})"

    def trapWeight(self):
        weight = self.damage + self.speed + (0.1 * self.aggroRange)
        weight = round(weight, 2)
        return weight
    
    def is_in_range(self, path):
        i=0
        #We need to figure out which way the arrow trap is facing, either left or right
        #We can find it based on the tiles, if there is a solid tile to the left, its facing right, vice versa
        trapX, trapY = self.position
        if self.grid[trapX + 1, trapY] in solidTiles and self.grid[trapX - 1, trapY] in solidTiles:
            #Bad arrow trap
            return None
        elif self.grid[trapX + 1, trapY] in solidTiles:
            #Facing left, due to a block to the right
            facingMultiplier = -1
        elif self.grid[trapX - 1, trapY] in solidTiles:
            #Facing right, due to a block to the left
            facingMultiplier = 1
        self.facingMultiplier = facingMultiplier

        for playerX, playerY in path:
            i+=1
            if playerY == trapY:  #Only check positions at the same height
                x_distance = (playerX - trapX) * facingMultiplier
                if 1 <= x_distance <= self.aggroRange:
                    self.playerPos = (playerX, playerY)
                    encounterSteps.append(i)
                    return (playerX, playerY)
        return None
    
    def compute_difficulty_score(self, enemyGrid):
        enemyX, enemyY = self.position
        playerX, playerY = self.playerPos
        #The arrow trap shoots an arrow at speed of 3 tiles ever 0.1s, so 30 tiles / s
        maxArrowTime = self.aggroRange / self.speed
        minArrowTime = 1 / self.speed
        totalTiles = abs(playerX - enemyX)
        timeToPlayer = totalTiles / self.speed
        difficultyScore = (maxArrowTime - timeToPlayer) / (maxArrowTime - minArrowTime)
        difficultyScore = max(0.2, difficultyScore)
        return difficultyScore

def checkTraps(path, enemyGrid):
    #All enemies present in the level
    allTraps = []
    #Enemies which aggro onto the Spelunker or get in the way
    activeTraps = []

    trapPotentialScores = []
    trapWeightedScores = []

    for (x, y), char in enemyGrid.items():
        if char == "s":
            allTraps.append(spikes((x, y)))
        elif char == "a":
            #We need enemyGrid to check the way the arrow trap is facing
            allTraps.append(ArrowTrap((x, y), enemyGrid))

    #Checking if any enemies are in range, and then calculating their difficulty
    for trap in allTraps:
        #Player position will be the first coordinate in path which is in range of that enemy
        player_position = trap.is_in_range(path)
        if player_position:
            activeTraps.append(trap)

            trap.difficulty_score = trap.compute_difficulty_score(enemyGrid)
            trapPotentialScores.append(trap.difficulty_score)

            weight = trap.trapWeight()
            weightedScore = weight * trap.difficulty_score
            weightedScore = round(weightedScore, 2)
            trapWeightedScores.append(weightedScore)
            trap.difficulty_score = trap.compute_difficulty_score(enemyGrid)

            activeTrapCount = len(activeTraps)
            allTrapCount = len(allTraps)

            #print(f"{type(trap).__name__} at {trap.position}, The difficulty score was: {trap.difficulty_score}")

    return encounterSteps, trapPotentialScores, trapWeightedScores, activeTrapCount, allTrapCount