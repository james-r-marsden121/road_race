#!/usr/local/bin/python3

import getCh


while True:
    key = getCh.getch()
    print ("Someone pressed the " + key)

    if (key == "A"):
        break

exit (0)
