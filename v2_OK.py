import os
import sys
import time
from tkinter import *
import tkinter.ttk as ttk 
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
    sv.set('Forward\n' + sv.get())

def move_backward(event):
    client_socket.send('\x03')
    sv.set('Backward\n' + sv.get())

def move_left(event):
    client_socket.send('\x05')
    sv.set('Left\n' + sv.get())

def move_right(event):
    client_socket.send('\x07')
    sv.set('Right\n' + sv.get())

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


root = Tk()
root.title('Control Interface')
largeur = 650
hauteur = 500
root.geometry('' + str(largeur) + 'x' + str(hauteur))
root.maxsize(largeur, hauteur)
root.resizable(width=False, height=False)

#Debut top--------------------------------------------------------------------------------

#Top application
top = Label(root, bg="gray7")
top.pack(anchor="n",fill=X)

#Affichage Logo
photo = PhotoImage(file = "Vroum2.png")
logo = Label(top, image= photo, bg="gray7")
logo.pack(anchor="nw", side=LEFT)

#Frame pour liste de commandes
frame_liste_commandes = Frame(top, height = 100, width=120, background="steel blue")
frame_liste_commandes.pack(anchor="ne",side= RIGHT, padx = 20, pady=20)

#Affichage liste commandes
liste_commande = Label(frame_liste_commandes, bg='navy',fg="white", text="Liste de commandes", font='Helvetica 12 bold', justify="center")
liste_commande.pack(anchor="n")
commande_haut = Label(frame_liste_commandes, text="↑ Haut", fg="black", font='Helvetica 12 ', background="steel blue")
commande_haut.pack()
commande_bas = Label(frame_liste_commandes, text="↓ Bas", fg="black", font='Helvetica 12 ', background="steel blue")
commande_bas.pack()
commande_gauche = Label(frame_liste_commandes, text="← Gauche", fg="black", font='Helvetica 12 ', background="steel blue")
commande_gauche.pack()
commande_droite = Label(frame_liste_commandes, text="→ Droite", fg="black", font='Helvetica 12 ', background="steel blue")
commande_droite.pack()

#Fin top--------------------------------------------------------------------------------

#Debut mid--------------------------------------------------------------------------------

#Mid application
mid = Label(root, height = 200, width=600, background="gray7")
mid.pack(anchor="center", fill=X)

#Variable texte pour l'historique
sv = StringVar()

#Historique des commandes
historique = Label(mid, textvariable=sv, font='Helvetica 12 ', fg='red', bg='steel blue',anchor=NW, width=20, height=15)
#scroll = Scrollbar(historique, orient='vertical')
#scroll.pack(anchor="e",side=RIGHT)
historique.pack(anchor="w",padx=20, side= LEFT)


#Frame pour stocker les flèches
frame_fleches = Frame(mid,height = 150, width=200, background="gray7")
frame_fleches.pack(anchor="center",side = LEFT, padx=60)

#Fleches
fleche_haut = Button(frame_fleches, text='↑', command = lambda: move_forward('<Up>'), width=3 , height= 3)
fleche_haut.pack(side=TOP)
fleche_gauche = Button(frame_fleches, text='←', command = lambda: move_left('<Left>'), width=3 , height= 3)
fleche_gauche.pack(side=LEFT)
fleche_bas = Button(frame_fleches, text='↓', command = lambda: move_backward('<Down>'), width=3 , height= 3)
fleche_bas.pack(side=LEFT)
fleche_droite = Button(frame_fleches, text='→', command = lambda: move_right('<Right>'), width=3 , height= 3)
fleche_droite.pack(side=LEFT)


#Frame pour stocker les boutons de démos
frame_demos=Frame(mid,height = 150, width=180, background="steel blue")
frame_demos.pack(anchor="e",side = LEFT, padx=20, fill=BOTH)

#Boutons pour lancer des démos (circuits)
liste_circuits = Label(frame_demos, bg='navy',fg="white", text="     Liste de circuits      ", font='Helvetica 12 bold')
liste_circuits.pack(anchor="n")
circuit_1 = Label(frame_demos, text="Circuit 1", fg="black", font='Helvetica 12 ', background="steel blue")
circuit_1.pack()
circuit_2 = Label(frame_demos, text="Circuit 2", fg="black", font='Helvetica 12 ', background="steel blue")
circuit_2.pack()
circuit_3 = Label(frame_demos, text="Circuit 3", fg="black", font='Helvetica 12 ', background="steel blue")
circuit_3.pack()
circuit_4 = Label(frame_demos, text="Circuit 4", fg="black", font='Helvetica 12 ', background="steel blue")
circuit_4.pack()

#Fin top--------------------------------------------------------------------------------

#Debut bot--------------------------------------------------------------------------------

#Bot application
bot = Label(root, height = 200, width=600, background="gray7")
bot.pack(anchor="s", fill=X)

#Variable texte pour état voiture
"""
text_state_car = StringVar()
text_state_car.set("Etat de la voiture")
"""
lb_connect = LabelFrame(root, bg='green')
lb_connect.pack(anchor="w",side = LEFT, padx=20,pady=10)
en_connect = Entry(lb_connect)
en_connect.insert(0, "Etat de la voiture")
en_connect.pack()

""" TODO """
# Label état voiture connectée
#state_car=Label(bot,height = 30,textvariable=text_state_car, width=40,fg='red', bg='steel blue',anchor=W)
#state_car.pack(anchor="w",side = LEFT, padx=20,pady=10)



#Frame pour stocker liste deroulante des voitures et bouton login
frame_connexion=Frame(bot,height = 150, width=250, background="steel blue")
frame_connexion.pack(anchor="e",side = RIGHT, padx=20,pady=10)

#liste voitures
voitures=["beewi mini cooper","beewi fiat 500"]

#liste deroulante
choix_voitures = ttk.Combobox(frame_connexion, values=voitures)
choix_voitures.pack (side=LEFT,padx=5)

# Récupère le nom de la voiture souhaitée
login = Button(frame_connexion, text='Log in', command = lambda: f_connect(choix_voitures.get()))
login.pack(side=RIGHT, padx=5)

#Fin bot--------------------------------------------------------------------------------

# listeners des flèches au clavier
root.bind('<Left>', move_left)
root.bind('<Right>', move_right)
root.bind('<Up>', move_forward)
root.bind('<Down>', move_backward)

# affichage de l'interface
mainloop()


###########################################################################
