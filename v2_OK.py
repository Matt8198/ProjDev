
import os
import sys
import time
from tkinter import *
import tkinter.ttk as ttk 
from bluetooth import *

# Socket pour 1 connexion bluetooth
waitForBluetooth = True
while waitForBluetooth :
    try :
        client_socket = BluetoothSocket( RFCOMM )
        client_socket.bind(("", PORT_ANY))  # TODO une deuxième, tester en simultané
        waitForBluetooth = False
        # nbConnections à MAJ en fct du nb de clics sur Connect ?
    except OSError :
        print("Votre Bluetooth n'est pas activé !")
        waitForBluetooth = True
        time.sleep(5)

# STOP Forward  ↑ - \x00
# Forward  ↑ - \x01
# STOP Backward ↓ - \x02
# Backward ↓ - \x03
# STOP Left ← - \x04
# Left      ← - \x05
# STOP Right→ - \x06
# Right     → - \x07

# Repositionne les roues droites
def reset_wheels():
    client_socket.send('\x04')  # STOP Left
    client_socket.send('\x06')  # STOP Right

# Les fonctions "stop_...()" stoppent d'abord les autres mouvements avant de faire l'action souhaitée
def stop_before_backward():
    reset_wheels()
    client_socket.send('\x00')  # STOP Forward

def stop_before_forward():
    reset_wheels()
    client_socket.send('\x02')  # STOP Backward

"""
Bind des touches :
    A : Reculer et tourner à gauche
    E : Reculer et tourner à droite
    Z : Avancer en ligne droite
    S : Reculer en ligne droite
    Q : Avancer et tourner à gauche
    D : Avancer et tourner à droite
"""
def move_forward():
    try:
        stop_before_forward()  # reset current moves
        client_socket.send('\x01')  # avance en ligne droite
        sv.set('Forward\n' + sv.get())
    except OSError :
        text_state_car.set("You are not connected !")
        
def move_backward():
    try:
        stop_before_backward()  # reset current moves
        client_socket.send('\x03')  # recule en ligne droite
        sv.set('Backward\n' + sv.get())
    except OSError :
        text_state_car.set("You are not connected !")
        
def forward_to_left():
    try:
        client_socket.send('\x05')  # Tourne à gauche
        client_socket.send('\x01')  # Avance
        sv.set('Forward Left\n' + sv.get())
    except OSError :
        text_state_car.set("You are not connected !")
        
def forward_to_right():
    try:
        client_socket.send('\x07')  # Tourne à droite
        client_socket.send('\x01')  # Avance
        sv.set('Forward Right\n' + sv.get())
    except OSError :
        text_state_car.set("You are not connected !")

def backward_to_left():
    try:
        client_socket.send('\x05')  # Tourne à gauche
        client_socket.send('\x03')  # Avance
        sv.set('Backward Left\n' + sv.get())
    except OSError :
        text_state_car.set("You are not connected !")
        
def backward_to_right():
    try:
        client_socket.send('\x07')  # Tourne à droite
        client_socket.send('\x03')  # Avance
        sv.set('Backward Right\n' + sv.get())
    except OSError :
        text_state_car.set("You are not connected !")

###########################################################################
# Bluetooth scanning
appareilsDispo = []
def f_scan():
    # TODO gérer si le Bluetooth est désactivé !
    text_state_car.set('Start scanning')
    appareilsDetectes = discover_devices(lookup_names=True, duration=3,
                                         flush_cache=True)
    # Liste des appareils proches
    appareilsDispo.clear()
    for _mac, _name in appareilsDetectes:
        # Filtre seulement les appareils "beewi"
        if "beewi" in _name.lower():
            print(_mac, " ", _name)
            print("_name = ", _name)
            appareilsDispo.append((_mac, _name))

    # Met à jour la liste des véhicules disponibles
    choix_voitures['values'] = [appareil[1] for appareil in appareilsDispo]
    # Maintenant on peut selectionner une voiture :
    choix_voitures['state'] = "enabled"
    btn_connect['state'] = NORMAL

# Bluetooth connection   
def f_connect():
    car = []
    selectedCar = choix_voitures.current()
    try :
        car = appareilsDispo[selectedCar]
        # Connexion à la voiture
        # TODO : Gérer @mac pour plusieurs voitures
        _macaddr = car[0]
    except IndexError:  # outofbounds
        text_state_car.set('Please enable Bluetooth on your laptop !')

    if (car != []):
        text_state_car.set(car[1] +' detected')
        try :
            client_socket.connect((_macaddr, 1))
            text_state_car.set("Connection successful")
        except OSError:
            # Gère une erreur de connexion
            text_state_car.set("Connection ERROR ! Device is not ON/available")

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

# Boutons de contrôle de l'interface graphique
fleche_back_gauche = Button(frame_fleches, text='←|', command = lambda: backward_to_left(), width=3 , height= 3)
fleche_back_gauche.pack(side=RIGHT)
fleche_haut = Button(frame_fleches, text='↑', command = lambda: move_forward(), width=3 , height= 3)
fleche_haut.pack(side=TOP)
fleche_back_droite = Button(frame_fleches, text='|→', command = lambda: backward_to_right(), width=3 , height= 3)
fleche_back_droite.pack(side=RIGHT)

fleche_gauche = Button(frame_fleches, text='←', command = lambda: forward_to_left(), width=3 , height= 3)
fleche_gauche.pack(side=LEFT)
fleche_bas = Button(frame_fleches, text='↓', command = lambda: move_backward(), width=3 , height= 3)
fleche_bas.pack(side=LEFT)
fleche_droite = Button(frame_fleches, text='→', command = lambda: forward_to_right(), width=3 , height= 3)
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
text_state_car = StringVar()
text_state_car.set("Etat de la voiture")
lb_connect = LabelFrame(root, bg='green')
lb_connect.pack(anchor="w",side = LEFT, padx=20,pady=10)

# Label état voiture connectée
state_car=Label(bot,height = 30,textvariable=text_state_car, width=40,fg='red', bg='steel blue',anchor=W)
state_car.pack(anchor="w",side = LEFT, padx=20,pady=10)

#Frame pour stocker liste deroulante des voitures et bouton login
frame_connexion=Frame(bot,height = 150, width=250, background="steel blue")
frame_connexion.pack(anchor="e",side = RIGHT, padx=20,pady=10)

#liste deroulante pour le choix de la voiture à connecter
choix_voitures = ttk.Combobox(frame_connexion, values=[],
                              state="disabled")  # readonly au départ car aucune voiture n'a été détéctée pour le moment
choix_voitures.pack(side=LEFT,padx=5)

# Connexion à une voiture une fois séléctionnée
btn_connect = Button(frame_connexion, text='Connect', command = lambda: f_connect(), state=DISABLED)
btn_connect.pack(side=RIGHT, padx=5)

# Scan des appareils "beewi" bluetooth proches
scan = Button(frame_connexion, text='BT Scan', command = lambda: f_scan())
scan.pack(side=RIGHT, padx=5)

#Fin bot--------------------------------------------------------------------------------

# listeners des flèches au clavier
root.bind('<a>', forward_to_left)
root.bind('<e>', forward_to_right)
root.bind('<q>', forward_to_right)
root.bind('<d>', forward_to_right)
root.bind('<z>', move_forward)
root.bind('<s>', move_backward)

# affichage de l'interface
mainloop()


###########################################################################
