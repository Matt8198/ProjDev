
import os
import sys
import time
from tkinter import *
from bluetooth import *

_macaddr = None
client_socket = BluetoothSocket( RFCOMM )

# Forward  ↑ - \x01
# Backward ↓ - \x03
# Left     ← - \x05
# Right    → - \x07

# Fonction réservée à l'affichage des commandes dans l'historique
def set_text(e,text):
    e.delete(0,END)
    e.insert(0,text)

# Les fonctions "move_...()" orientent la voiture selon la direction souhaitée
def move_forward(event):
    client_socket.send('\x01')
    sv.set(sv.get() + 'Forward\n')

def move_backward(event):
    client_socket.send('\x03')
    sv.set(sv.get() +'Backward\n')

def move_left(event):
    client_socket.send('\x05')
    sv.set(sv.get() + 'Left\n')

def move_right(event):
    client_socket.send('\x07')
    sv.set(sv.get() + 'Right\n')

# TODO Centraliser dans une seule fonction move() ?
# Les évènements reçus pour les clics(boutons ou les flèches) sont différents
def move_arrows(event):
    # Commander la voiture avec les flèches
    if event.keysym == 'Up' :
        move_forward(event)
    elif event.keysym == 'Down' :
        move_backward(event)
    elif event.keysym == 'Left' :
        move_left(event)
    else :
        move_right(event)

# Deplacement avec les boutons de l'interface graphique
def move_buttons(event):
    if event == 'Up' :
        move_forward(event)
    elif event == 'Down' :
        move_backward(event)
    elif event == 'Left' :
        move_left(event)
    else :
        move_right(event)

###########################################################################
# Bluetooth scanning
def f_connect(name):
    set_text(en_connect,'Start scanning')
    res = discover_devices(lookup_names=True)

    for _mac, _name in res:
        # Scanne la voiture dont le nom est la valeur du paramètre
        # Exemple : beewi mini cooper
        if (_name.lower().startswith(name)):
            _macaddr = _mac
            set_text(en_connect, name + ' detected')
            res = client_socket.connect((_macaddr, 1))
            set_text(en_connect, "Connection successful")
        else:
            set_text(en_connect,name + ' not detected')
###########################################################################
"""
client_socket.close()  # TODO : IF closed -> Refresh texte : "Connection successfull" -> "Enter a device name"
					   # => Liste de choix des voitures au lieu de saisir !!!
					   # avec une map par exemple : 1 = "beewi mini cooper", 2 = "fiat 500" ...
"""
###########################################################################
# Tkinter

# Fenêtre principale
win = Tk()
win.title('Control Interface')
largeur = 1200
hauteur = 700
win.geometry('' + str(largeur) + 'x' + str(hauteur))
win.maxsize(largeur, hauteur)
win.resizable(width=False, height=False)

# Partie commande
lb_command = LabelFrame(win, bg='blue')
lb_command.grid(row=1, column=1, padx=150, pady=200)
sv = StringVar()
# Label pour afficher la liste des commandes en attente (historique)
la_hist = Label(lb_command, textvariable=sv, font='Helvetica 12 bold', fg='red', bg='purple', padx=20)
la_hist.grid(row=1, column=1, rowspan=3)


# Flèches pour contrôler
bu_up = Button(lb_command, text='↑', command = lambda: move_buttons('Up'))
bu_up.grid(row=2, column=3)
bu_left = Button(lb_command, text='←', command = lambda: move_buttons('Left'))
bu_left.grid(row=3, column=2)
bu_down = Button(lb_command, text='↓', command = lambda: move_buttons('Down'))
bu_down.grid(row=3, column=3)
bu_right = Button(lb_command, text='→', command = lambda: move_buttons('Right'))
bu_right.grid(row=3, column=4)

# Label pour la liste des commandes
lb_informa = LabelFrame(win, bg='red')
lb_informa.grid(row=1, column=2, padx=5)
la_divers = Label(lb_informa, text='bonjour', font='Helvetica 12 bold', fg='red', bg='purple', padx=20)
la_divers.grid(row=1, column=1)
la_colist = Label(lb_informa, text='Forward ↑ Backward ↓ Left ← Right →', font='Helvetica 12 bold', fg='red', bg='purple', padx=20)
la_colist.grid(row=2, column=1)

# Label pour la connexion à une voiture avec son nom
lb_connect = LabelFrame(win, bg='green')
lb_connect.grid(row=2, column=1, padx=5)
en_connect = Entry(lb_connect)
en_connect.insert(0, 'beewi mini cooper')
en_connect.grid(row=1, column=1, padx=5)
# Récupère le nom de la voiture souhaitée et se connecte
bu_connect = Button(lb_connect, text='Log in', command = lambda: f_connect(en_connect.get()))
bu_connect.grid(row=1, column=2, padx=5)

# listeners des flèches au clavier
win.bind('<Left>',  move_arrows)
win.bind('<Right>', move_arrows)
win.bind('<Up>',    move_arrows)
win.bind('<Down>',  move_arrows)

# affichage de l'interface
win.mainloop()

###########################################################################
