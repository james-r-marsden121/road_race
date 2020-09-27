import os
import random
import time
import threading
import KeyPoller
import bcolors

class RoadRace ():

    def __init__ (self):
        self.myLineCount      = 1
        self.myScore          = 0
        self.myTopScore       = 0
        self.myTopScorer      = ""
        self.myOtherCar       = False
        self.myOtherCarOffset = 0
        self.myStillAlive     = True
        self.myRoadOffset     = int (random.random()*60)

        # This stores the road printed so far, as an indexed dict object
        self.myRoadScreen     = {0: ""}
        self.myCar            = bcolors.bcolors.RED + "H" + bcolors.bcolors.ENDC

        # What do these do - TCB
        self.myVarA      = 38 # Code (" ")
        self.myVarF      = self.myVarA
        self.myVarB      = 24 # Code "+" # The row location to print the road
        self.myVarC      = 1  # Code "G Shft + 1" # A fixed constant

        # Location of the road-offset
        self.myVarN      = 3  # Code "G Shft + 7"

        # Location variables are X & Y - X being up / down & Y is left right
        # Z is the previous value of Y
        self.myVarX      = 9  # Code GH - location is 9 rows down
        self.myVarY      = self.myVarX + self.myRoadOffset
        self.myVarZ      = self.myVarY

        self.getTopScore ()

        return

    def startRace (self):
        if (os.name == "nt"):
            os.system("cls")
        else:
            os.system("clear")

        self.printStartRace ()

        while (self.myStillAlive == True):
            self.randomizeRoadLeftRight ()
            self.getKey ()
            self.addCarsToRoad()
            self.printScore ()
            #self.printMyRoadOffset ()
            self.printMyCar ()
            self.printRoad ()
            self.checkCollision ()
            self.setMyCarPrev ()

        self.gameOverRoutine ()

        return

    def randomizeRoadLeftRight (self):
        # line 90
        # LET N=N+(SGN(CODE (G5) - INT (RND* CODE (GS))))*(N<>A)*(N<>X)+(N=A)-(N-X)
        # Graphic 5 (G5) =  5
        # Graphic S (GS) =  10
        # SGN returns either 1 or -1 (or 0 if input is 0)

        myRandNo     = int (random.random() * 10)
        myRandOffSet = self.getSign (5 - myRandNo)

        self.myRoadOffset = self.myRoadOffset + myRandOffSet

        # Don't allow the offset to get too big or too small beause
        # otherwise the road would slip off the side of the screen

        if (self.myRoadOffset < 0):
            self.myRoadOffset = 0
        elif (self.myRoadOffset) > 64:
            self.myRoadOffset = 64

        return

    def captureKeyLeftRight (self, myKeyStroke):
        # line 110

        if myKeyStroke  == "o":
            #print ("Left Key")
            self.myVarZ = self.myVarY
            self.myVarY = self.myVarY - 1
        elif myKeyStroke  == "p":
            #print ("Right Key")
            self.myVarZ = self.myVarY
            self.myVarY = self.myVarY + 1
        else:
            self.myVarZ = self.myVarY

        return

    def getKey (self):
        myLoopCount = 10

        with KeyPoller.KeyPoller() as keyPoller:
            while (myLoopCount != 0):
                myKey = keyPoller.poll()
                #print ("Polling " + str (myLoopCount))

                if not myKey is None:
                    self.captureKeyLeftRight (myKey)

                myLoopCount = myLoopCount - 1
                time.sleep (0.04)

        return

    def addCarsToRoad (self):
        # line 120
        # IF RND > .8 THEN PRINT AT B-C, N + INT (RND * 3 + C); "H"
        myRandNo = random.random()
        myRandOffSet = random.randrange(0,6)

        if myRandNo > 0.8:
            self.myOtherCar       = True
            self.myOtherCarOffset = myRandOffSet + 1 + 4
        else:
            self.myOtherCar       = False
            self.myOtherCarOffset = 0

        return

    def printRoad (self):
        # line 130
        # PRINT AT B, N-C; "XX____XX"; AT X,Y "H"; AT X-C,Z; "_"; AT X+C,Y
        # LET F = F + C
        myRoadWall = chr (0x2588)

        if (self.myScore < 20):
            myRoadSurface = chr (0x259a)
        else:
            myRoadSurface = chr (0x2592)

        myTmpOffset   = self.myRoadOffset
        myLeftFiller  = chr (0x20) * self.myRoadOffset
        myRightFiller = chr (0x20) * (80 - len (myLeftFiller) - 4 - 8 - 4)

        myRoadBlock = myLeftFiller + myRoadWall * 4 + myRoadSurface * 8 + myRoadWall * 4 + myRightFiller

        if self.myOtherCar == True:
            myNewRoadBlock = "".join((myRoadBlock[:self.myRoadOffset + self.myOtherCarOffset],"H",myRoadBlock[self.myRoadOffset + self.myOtherCarOffset+1:]))
        else:
            myNewRoadBlock = myRoadBlock

        self.printAtLoc (self.myVarB, 1, myNewRoadBlock)
        self.captureRoad (myNewRoadBlock)

        return

    def captureRoad (self, myRoadBlock):
        # The code here needs to cature the road locations so that we can 
        # check the location later for collissions
        self.myRoadScreen.update ({self.myScore: myRoadBlock})

        return

    def checkCollision (self):
        # line 150 & 160
        # LET W = PEEK (PEEK 16398 + PEEK 16399 * 256)
        # IF W <> CODE ("X") AND W <> CODE ("H") THEN GOTO 80
        myCheck = True

        myCurrBlock = self.myRoadScreen.get(self.myScore - 130)
        myNextBlock = self.myRoadScreen.get(self.myScore - 140)

        if (myCurrBlock is None) or (myNextBlock is None):
            myCheck = False

        if (myCheck == True):
            if myNextBlock[self.myVarY - 1] == "H":
                self.myStillAlive = False
                self.printAtLoc (10, 25, "Driver crashed into another car!")

            if myNextBlock[self.myVarY - 1] == chr(0x2588):
                self.myStillAlive = False
                self.printAtLoc (10, 28, "Driver crashed into wall!")

            if myNextBlock[self.myVarY - 1] == chr(0x20):
                self.myStillAlive = False
                self.printAtLoc (10, 28, "Driver veered off course!")

        if (self.myStillAlive == True):
            self.myScore = self.myScore + 10

        return

    def printMyCar (self):
        # line 130
        # PRINT AT X-1,Y; "_"
        # PRINT AT X,Y; "H"
        self.printAtLoc (self.myVarX - 1, self.myVarZ, chr(9618))
        self.printAtLoc (self.myVarX, self.myVarY, self.myCar)

        return

    def setMyCarPrev (self):
        # This is used if the car wasn't moved left + right
        self.myVarZ = self.myVarY

        return

    def printAtLoc (self, myXLoc, myYLoc, myPrintStr):
        print ("\033["+str (myXLoc)+";"+str (myYLoc)+"H"+ myPrintStr)

        return

    def printScore (self):
        # The original game doesn't print the score until the end

        if (self.myRoadOffset < 32):
             tmpMyScorePlace = 50
        else:
             tmpMyScorePlace = 5

        tmpTopScoreLine = "Top Score : " + str (self.myTopScore) + \
                                             " (" + self.myTopScorer +")"
        tmpScoreLine    = "My Score  : " + str (self.myScore)
        tmpScoreReplace = chr (0x20) * len (tmpTopScoreLine)

        self.printAtLoc (21, tmpMyScorePlace, tmpScoreReplace)
        self.printAtLoc (22, tmpMyScorePlace, tmpTopScoreLine)
        self.printAtLoc (23, tmpMyScorePlace, tmpScoreLine)

        return

    def printMyRoadOffset (self):
        # This is a debugging routine
        self.printAtLoc (2, 60, "MyRoadOffset : " + str (self.myRoadOffset))

        return

    def getSign (self, myNumber):
        # This method recreates the SGN function from ZX81 basic, which
        # returns -1 for negative numbers, 1 for positve numbers and 0 for
        # the case of 0 being passed

        if (myNumber < 0):
            return -1
        
        if (myNumber > 0):
            return 1

        return 0

    def gameOverRoutine (self):
        # Print the game over message
        self.printGameOver ()

        # This logic captures the high-score and saves this to a disk file
        if (self.myScore > self.myTopScore):
            self.printAtLoc (24, 33, "New Top Score")
            self.myTopScore = self.myScore

            myTopFile = open ("./myTopScore.txt", "w")
            myScoreLine = str (self.myTopScore) + "," + "James"
            myTopFile.write (myScoreLine)

            myTopFile.close ()

    def getTopScore (self):
        # This routine loads the top score file if present
        try:
            myTopFile = open ("./myTopScore.txt", "r")
            myScoreLine = myTopFile.readline ()
            myTopFile.close ()

            self.myTopScore  = int (myScoreLine[0:myScoreLine.index(",")])
            self.myTopScorer = myScoreLine[myScoreLine.index(",")+1:len (myScoreLine)]
        except IOError:
            self.myTopScore  = 0
            self.myTopScorer = ""

        return

    def printStartRace (self):
        self.printAtLoc (24, 20, " #####   #######     #     ######   #######")
        self.printAtLoc (24, 20, "#     #     #       # #    #     #     #   ")
        self.printAtLoc (24, 20, "#           #      #   #   #     #     #   ")
        self.printAtLoc (24, 20, " #####      #     #     #  ######      #   ")
        self.printAtLoc (24, 20, "      #     #     #######  #   #       #   ")
        self.printAtLoc (24, 20, "#     #     #     #     #  #    #      #   ")
        self.printAtLoc (24, 20, " #####      #     #     #  #     #     #   ")
        self.printAtLoc (24, 20, "                                           ")
        self.printAtLoc (24, 21, "######      #      #####   #######   ###   ")
        self.printAtLoc (24, 21, "#     #    # #    #     #  #         ###   ")
        self.printAtLoc (24, 21, "#     #   #   #   #        #         ###   ")
        self.printAtLoc (24, 21, "######   #     #  #        #####      #    ")
        self.printAtLoc (24, 21, "#   #    #######  #        #               ")
        self.printAtLoc (24, 21, "#    #   #     #  #     #  #         ###   ")
        self.printAtLoc (24, 21, "#     #  #     #   #####   #######   ###   ")

        return

    def printGameOver (self):
        self.printAtLoc (12, 24, " #####      #     #     #  #######  ")
        self.printAtLoc (13, 24, "#     #    # #    ##   ##  #        ")
        self.printAtLoc (14, 24, "#         #   #   # # # #  #        ")
        self.printAtLoc (15, 24, "#  ####  #     #  #  #  #  #####    ")
        self.printAtLoc (16, 24, "#     #  #######  #     #  #        ")
        self.printAtLoc (17, 24, "#     #  #     #  #     #  #        ")
        self.printAtLoc (18, 24, " #####   #     #  #     #  #######  ")
        self.printAtLoc (19, 24, "                                    ")
        self.printAtLoc (20, 21, "#######  #     #  #######  ######    ###   ")
        self.printAtLoc (21, 21, "#     #  #     #  #        #     #   ###   ")
        self.printAtLoc (22, 21, "#     #  #     #  #        #     #   ###   ")
        self.printAtLoc (23, 21, "#     #  #     #  #####    ######     #    ")
        self.printAtLoc (24, 21, "#     #   #   #   #        #   #           ")
        self.printAtLoc (24, 21, "#     #    # #    #        #    #    ###   ")
        self.printAtLoc (24, 21, "#######     #     #######  #     #   ###   ")
        self.printAtLoc (24, 21, "                                    ")

        return
