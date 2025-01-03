# SpelunkyHD Level Difficulty Analysis Tool

This tool allows you to analyse the difficulty of SpelunkyHD levels. It takes an input level pack file, simulates player behaviours and paths, and generates a difficulty report based on enemy and trap metrics.

## Getting Started

### Steps to Run the Application with Existing Data:

1. **Select a Level File**  
   Edit the `main.py` file, replacing the file names in the `main` function with the names of the existing levels you want to test.

2. **Run the Script**  
   Execute the `main.py` script to generate the difficulty report.

---

### To Test with Your Own Custom Levels:

1. **Download Frozlunky**  
   Get Frozlunky, a mod for Spelunky, from [Sashavol's Frozlunky page](https://sashavol.github.io/Frozlunky).

2. **Install SpelunkyHD**  
   Acquire SpelunkyHD, preferably through Steam. Set the version to `1_4` by using the properties tab for the game in Steam.

3. **Launch SpelunkyHD and Frozlunky**  
   Open SpelunkyHD (version `1_4`) and, during its launch, open the Frozlunky executable. It might take a few tries as Frozlunky doesn't always open on the first attempt.

4. **Create a Custom Level Pack**  
   - Once Frozlunky is open, click the "Switch to Level Editor" button.  
   - Use the editor to create your custom level pack.  
   - Test your levels by selecting the "Force Level to Game" checkbox.

5. **Save Your Level Pack**  
   Save your level pack and change its file extension from `.xml` to `.txt`.

6. **Prepare Your Level File**  
   - Locate your level(s), strip the XML tags, and save the new text file.  
   - The result should look like the following example:  
     ```
     00000000000000000000000111000000011100000000000000000000000000011101111111110001
     00000000000000000000000000000000000000000000000000000000000000000111001111111111
     ```
     Ensure the file contains 16 lines in total.

7. **Run the `prepareLevelFile.py` Script**  
   Edit the `prepareLevelFile.py` file to set the input file name to your newly saved level. Run the script to convert your file.

8. **Analyse the Difficulty**  
   Follow the original two steps outlined above to run the difficulty assessment on your custom level.

---

## Notes
- Make sure you are using SpelunkyHD version `1_4` for compatibility.  
- Test levels in Frozlunky to ensure they behave as expected before running the analysis.
- The app does not work well with ladders or platform tiles yet, may be added in the future.

---

Enjoy analyzing and refining your SpelunkyHD levels!
