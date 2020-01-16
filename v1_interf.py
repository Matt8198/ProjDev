
import os
import sys
import time
from tkinter import *
from bluetooth import *

_macaddr = None

# Forward  ↑ - \x01
# Backward ↓ - \x03
# Left     ← - \x05
# Right    → - \x07

def set_text(e,text):
    e.delete(0,END)
    e.insert(0,text)

def move_forward(event):
    "client_socket.send( '\x01' )"
    sv.set(sv.get() + 'Forward\n')

def move_backward(event):
    "client_socket.send( '\x03' )"
    sv.set(sv.get() +'Backward\n')

def move_left(event):
    "client_socket.send( '\x05' )"
    sv.set(sv.get() + 'Left\n')

def move_right(event):
    "client_socket.send( '\x07' )"
    sv.set(sv.get() + 'Right\n')

###########################################################################
# Bluetooth scanning
def f_connect(name):

    set_text(en_connect,'Start scanning')
    res = discover_devices(lookup_names=True)

    for _mac, _name in res:
        if (_name.lower().startswith(name)):
            _macaddr = _mac
            set_text(en_connect, name + ' detected')
            client_socket = BluetoothSocket( RFCOMM )
            res = client_socket.connect((_macaddr, 1))
            set_text(en_connect, "Connection successful")
        else:
            set_text(en_connect,name + ' not detected')

###########################################################################
"""
###########################################################################
# Testing
client_socket.send( '\x01' )
print("\t\t~ Forward")
time.sleep(0.5)
client_socket.send( '\x03' )
print("\t\t~ Backward")
time.sleep(0.5)
client_socket.send( '\x05' )
print("\t\t~ Left")
time.sleep(0.5)
client_socket.send( '\x07' )
print("\t\t~ Right")
time.sleep(0.5)
###########################################################################

client_socket.close()
"""
###########################################################################
# Tkinter

win = Tk()
win.title('Control Interface')

lb_command = LabelFrame(win, bg='blue')
lb_command.grid(row=1, column=1, padx=5)
sv = StringVar()
la_hist = Label(lb_command, textvariable=sv, font='Helvetica 12 bold', fg='red', bg='purple', padx=20)
la_hist.grid(row=1, column=1, rowspan=3)
bu_up = Button(lb_command, text='↑', command = lambda: move_forward('<Up>'))
bu_up.grid(row=2, column=3)
bu_left = Button(lb_command, text='←', command = lambda: move_left('<Left>'))
bu_left.grid(row=3, column=2)
bu_down = Button(lb_command, text='↓', command = lambda: move_backward('<Down>'))
bu_down.grid(row=3, column=3)
bu_right = Button(lb_command, text='→', command = lambda: move_right('<Right>'))
bu_right.grid(row=3, column=4)

lb_informa = LabelFrame(win, bg='red')
lb_informa.grid(row=1, column=2, padx=5)
la_divers = Label(lb_informa, text='bonjour', font='Helvetica 12 bold', fg='red', bg='purple', padx=20)
la_divers.grid(row=1, column=1)
la_colist = Label(lb_informa, text='Forward ↑ Backward ↓ Left ← Right →', font='Helvetica 12 bold', fg='red', bg='purple', padx=20)
la_colist.grid(row=2, column=1)

lb_connect = LabelFrame(win, bg='green')
lb_connect.grid(row=2, column=1, padx=5)
en_connect = Entry(lb_connect)
en_connect.insert(0, 'beewi mini cooper')
en_connect.grid(row=1, column=1, padx=5)
bu_connect = Button(lb_connect, text='Log in', command = lambda: f_connect(en_connect.get()))
bu_connect.grid(row=1, column=2, padx=5)

# listeners des flèches au clavier
win.bind('<Left>', move_left)
win.bind('<Right>', move_right)
win.bind('<Up>', move_forward)
win.bind('<Down>', move_backward)

win.mainloop()

###########################################################################
