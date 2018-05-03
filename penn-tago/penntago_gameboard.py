############################################################
#### This code is adapted from the Pentago MinMax AI written
#### in Java by Waylon Brown and available on GitHub
############################################################
import numpy as np

class GameBoard:
    slots = [[]]
    lastMove = ""	##move that defines this board compared to the parent of this board in the game tree
	
    def GameBoard():
         slots = np.zeros((6,6)).tolist()
         blankBoard()
	
	##used for copying game board moves
    def GameBoard(moves):
         slots = np.zeros((6,6)).tolist()
         for i in range(0,6):
              for j in range(0,6):
                  slots[i][j] = moves[i][j]
	
    def setLastMove(move):
        lastMove = move
    
    def makeMove(player, row, col):
		##use -1 since input is from 1-6, not 0-5
        slots[row - 1][col - 1] = player
	
    def isValidMove(row, col):
        return (slots[row - 1][col - 1] == 0)
	
	##rotate matrix clockwise
    def rotateClockwise(mat):
        mat = np.array(mat)
        ret = np.rot90(mat,  k=1, axes=(1, 0)).tolist()
        return ret
		
	##rotate matrix counter-clockwise
    def rotateCounterClockwise(mat):
        mat = np.array(mat)
        ret = np.rot90(mat,  k=1, axes=(0, 1)).tolist()
        return ret
	
	##used for minimax algorithm to determine how "good" a gameboard is
    def getUtility():
       
        utility = 0
        streak = 0  	##streak is used to add additional points for more than 2 in a row
								##2 in a row = 1 pt, 3 in a row = 2 pt, etc.
		
		##count horizontal doubles
        for i in range(0,6):	
         ##go down row
         for j in range(0,5):	
            ##count doubles
            if(slots[i][j] == 2 and slots[i][j+1] == 2):
                utility += streak + 1
                streak +=1
            else:
                streak = 0
		
		##count vertical doubles
        for i in range(0,6):	
         ##go down column
         for j in range(0,5):	
            ##count doubles
            if(slots[j][i] == 2 and slots[j+1][i] == 2):
                utility += streak + 1
                streak +=1
            else:
                streak = 0
		
		##count main diagonal up-left to down-right
        for i in range(0,5):
            if (slots[i][i] == 2 and slots[i+1][i+1] == 2):
                utility += streak + 1
                streak += 1
            else:
                streak = 0
		
		##count main diagonal up-right to down-left
        for i in range(0,5):
            if (slots[i][5-i] == 2 and slots[i+1][4-i] == 2):
                utility += streak + 1
                streak += 1
            else:
                streak = 0
        
        return utility
	
	##gets all children to this board, i.e. all next possible moves in the game
    def getChildren():
        #
		## original code: ArrayList<GameBoard> returnList = new ArrayList<GameBoard>();
		
		 
         returnList = []
         
         ############################################################
		  ##do this for each orientation of each quadrant of the board
		  ############################################################
         for rotation_dir in ["A", "B", "C", "D", "a", "b", "c", "d"]:
             for i in range(1,7):
                 for j in range(1,7):
                     if(isValidMove(i, j)):
                         tempBoard = GameBoard(slots)
                         tempBoard.makeMove(2, i, j)	 ##use 2 as it is for the AI's move
                         tempBoard.rotate(rotation_dir)
                         tempBoard.setLastMove(i + " " + j + " " + rotation_dir)
                         returnList.append(tempBoard)
         return returnList
	
    def printBoard():
        print("Current board:\n")
        for i in range(0,len(slots)):
            lineString = ""
            for j in range(0,len(slots[i])):
                if(slots[i][j] == 1):
                    lineString += "W "
                elif(slots[i][j] == 2):
                    lineString += "B "
                else:
                    lineString += "0 "
                if(j == 2):	##adds vertical middle split to board
                    lineString += "| "
            print(lineString)
            if(i == 2):	 ##adds horizontal middle split to board
                print("-------------")
	
    def blankBoard():
        for i in range(0,len(slots)):
            for j in range(0,len(slots[i])):
                slots[i][j] = 0
	
    def getLastMove():
        return lastMove
    
    def rotate(key):
        if (rotation_dir == "A") or (rotation_dir == "a"):
            xstart = 0
            ystart = 0
        elif (rotation_dir == "B") or (rotation_dir == "b"):
            xstart = 0
            ystart = 3
        elif (rotation_dir == "C" or (rotation_dir == "c")):
            xstart = 3
            ystart = 0
        elif (rotation_dir == "D") or (rotation_dir == "d"):
            xstart = 3
            ystart = 3
        
        quadrant = [[]]
        for i in range(0, 3):
            for j in range(0, 3):
                quadrant[i][j] = slots[xstart+i][ystart+j]
        
        if (key in ['a', 'b', 'c', 'd']):
            quadrant = rotateClockwise(quadrant)
        else:
            quadrant = rotateCounterClockwise(quadrant)
            
        for i in range(0, 3):
            for j in range(0, 3):
                slots[xstart+i][ystart+j] = quadrant[i][j]

		
	
	#returning 0 = no winner so far
	#returning 1 = first player (white) wins
	#returning 2 = second player (black) wins
    def determineWinner():
		##check rows
        
                
