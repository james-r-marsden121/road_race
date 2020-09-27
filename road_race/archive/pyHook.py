#!/opt/python3.7.4/bin/python3

import pyxhook

def OnKeyPress(event):
    print (event.Key)


    if event.Ascii == 32:
        exit(0)

hm = pyxhook.HookManager()
hm.KeyDown = OnKeyPress

hm.HookKeyboard()

hm.start()
