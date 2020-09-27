#!/usr/local/bin/python3

import getCh


class getKeyStrokes:

    def __init__ (self, myRoadRace):
        self.myRoadRace = myRoadRace

        return

    def getKey (self):
        while (True):
            key = getCh.getch()

            if (key == "Q"):
                break

            self.myRoadRace.captureKeyLeftRight (key)

