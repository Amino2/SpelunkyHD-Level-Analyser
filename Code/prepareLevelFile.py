def process_chunk(chunkLines):
    chunkSize = 10  #This is 10 due to the width of each room horizontally
    num_chunks = len(chunkLines[0]) // chunkSize
    result = []

    for chunkIndex in range(num_chunks):
        concatenated_line = ''
        for line in chunkLines:
            startIndex = chunkIndex * chunkSize
            concatenated_line += line[startIndex:startIndex + chunkSize]
        result.append(concatenated_line)
    
    return result

def main():
    inFile = 'Data/analysingFroz.txt'
    outFile = 'Data/processedFroz.txt'
    
    #Read input file
    with open(inFile, 'r') as file:
        text_block = file.read().strip()
    
    #Split the text block into lines
    lines = text_block.splitlines()
    
    #This is done in chunks of 4 due to the way Frozlunky stores the level data as a txt.
    all_results = []
    for chunk_start in range(0, len(lines), 4):
        chunk_lines = lines[chunk_start:chunk_start + 4]
        chunk_result = process_chunk(chunk_lines)
        all_results.extend(chunk_result)
    
    translatedLetters = []

    #We want to make the results easier to understand, so we change some characters:
    #all 0s will become " " to make it easier to see where solid blocks are in the level
    mappingTable = str.maketrans({'2': '1', 'C': '1', 'I': ' ', 'A': '1', '0': ' '})
    for letter in all_results:
        currentTLetter = letter.translate(mappingTable)
        translatedLetters.append(currentTLetter)

    #Now we add borders:
    topBotBorder = ['########################################']
    sideBorder = '###'
    translatedLetters = topBotBorder + topBotBorder + topBotBorder + translatedLetters + topBotBorder + topBotBorder + topBotBorder

    for i in range(len(translatedLetters)):
        translatedLetters[i] = sideBorder + translatedLetters[i] + sideBorder


    #Output results to txt file
    with open(outFile, 'w') as file:
        for line in translatedLetters:
            file.write(line + '\n')

if __name__ == '__main__':
    main()