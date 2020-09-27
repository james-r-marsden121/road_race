#! /usr/local/bin/python3

import KeyPoller
import time

with KeyPoller.KeyPoller() as keyPoller:
    while True:
        c = keyPoller.poll()
        if not c is None:
            if c == "c":
                break
            print (c)
        else:
            print ("Waiting for key press")
            time.sleep (2)
