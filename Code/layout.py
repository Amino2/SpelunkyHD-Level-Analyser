
def fallCheck(grid):
    vColLengths = []
    seenVcoordinates = []
    totalFallDistance = 0

    for (x, y), char in grid.items():
        if char == 'v' and (x, y) not in seenVcoordinates:
            #Start counting consecutive v's which denote a path the player took and was falling
            count = 0
            current_y = y
            while (x, current_y) in grid and grid[(x, current_y)] == 'v':
                count += 1
                seenVcoordinates.append((x, current_y))
                current_y += 1

            #Add the count to the list if > 0
            if count > 0:
                vColLengths.append(count)
                totalFallDistance += count

    fallDamageCount = 0

    for value in vColLengths:
        if value >=8:
            fallDamageCount +=1
    
    #Can be used in the future
    averageFallDistance = round((totalFallDistance / len(vColLengths)), 2)
    return vColLengths

