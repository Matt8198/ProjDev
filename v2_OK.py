import os
import sys
import time
from copy import deepcopy
from tkinter import *
import tkinter.ttk as ttk 
from bluetooth import *

# Initialise n emplacements pour des sockets Bluetooth
appareils_connectes = [None] * 3  # 3 Voitures simultannées au maximum
macro_rec = []

# Créé une socket Bluetooth
class Bluetooth :

    def __init__(self):
        self.socket = BluetoothSocket(RFCOMM)

    def connect(self, macaddr):
        self.socket.connect((macaddr, 1))
        print("Voiture connectée !")

    def send(self, ordre):
        self.socket.send(ordre)

    # Arrete la connexion Bluetooth
    def close(self, selectedCar):
        try :
            print("Appareils AVANT SUPPR : ", appareils_connectes)
            self.socket.close() # Ferme la socket de communication
            # TODO : Vérifier qu'on ferme bien la bonne socket !!
            #appareils_connectes[selectedCar].close()
            appareils_connectes[selectedCar] = None  # Supprime la voiture des appareils connectés
            print("Appareils APRES SUPPR : ", appareils_connectes)
        except OSError :
            print("Erreur de déconnexion !")

# Une socket Bluetooth
def connectNewDevice(macaddr, selectedCar) :
    new_socket = Bluetooth()
    print("selectedCar = ", selectedCar)
    if appareils_connectes[selectedCar] == None :
        #print("appareils_connectes[selectedCar] = ", appareils_connectes[selectedCar])
        try :
            new_socket.connect(macaddr)
            appareils_connectes[selectedCar] = new_socket  # enregistre la socket dans notre liste d'appareils connectés
        except OSError:
            # Gère une erreur de connexion, si on désactive le bluetooth après le scan
            text_state_car.set("Connection ERROR ! Device is not ON/available")
    else :
        print("Vous êtes déjà connecté à cet appareil !")

# Déconnexion d'une socket
def disconnectDevice(selectedCar):
    appareils_connectes[selectedCar].close(selectedCar)
    # TODO : IF closed -> Refresh affichage graphique : "Connection successful" -> "Enter a device name"

###########################################################################
# Bluetooth scanning
appareilsDispo = []
def f_scan():
    text_state_car.set('Start scanning')
    appareilsDetectes = discover_devices(lookup_names=True, duration=2)
    # Liste des appareils proches
    appareilsDispo.clear()
    # TODO : La liste des appareils PROCHES, pas les appareils déjà accouplés
    for _mac, _name in appareilsDetectes:
        # Filtre seulement les appareils "beewi"
        if "beewi" in _name.lower():
            print(_mac, " ", _name)
            appareilsDispo.append((_mac, _name))

    # Met à jour la liste des véhicules disponibles
    for appareil in appareilsDispo:
        if appareil[1] not in choix_voitures['values']:
            # Ajoute un nouveau véhicule à la fin de la liste de choix
            choix_voitures['values'] = (*choix_voitures['values'], appareil[1])

    # Maintenant on peut selectionner une voiture :
    choix_voitures['state'] = "enabled"
    btn_connect['state'] = NORMAL

# Bluetooth connection
def f_connect():
    car = []
    selectedCar = choix_voitures.current()
    choix_voitures['state'] = "disabled"
    # Assure qu'on ait choisi une voiture parmi les choix disponibles
    if selectedCar != -1 : 
        try :
            car = appareilsDispo[selectedCar]
            # Connexion à la voiture
            # TODO : Gérer @mac pour plusieurs voitures
            macaddr = car[0]
        except IndexError:  # outofbounds
            text_state_car.set('Please enable Bluetooth on your laptop !')

        if (car != []):
            text_state_car.set(car[1] +' detected')
            # Enregistre la socket associée à la voiture connectée
            connectNewDevice(macaddr, selectedCar)  # passe le numéro de la voiture (indice de la liste de choix)
            text_state_car.set("Connection successful")


###########################################################################
###########################################################################

"""
    - STOP Forward  - \x00
    - Forward       - \x01
    - STOP Backward - \x02
    - Backward      - \x03
    - STOP Left     - \x04
    - Left          - \x05
    - STOP Right    - \x06
    - Right         - \x07
"""

# Repositionne les roues droites
def reset_wheels(selectedCar):
    try:
        appareils_connectes[selectedCar].send('\x04')  # STOP Left
        appareils_connectes[selectedCar].send('\x06')  # STOP Right
    except (OSError, AttributeError) as e :
        text_state_car.set("You are not connected !")
        print(e)
        
"""
    Les fonctions "stop_...()" arrêtent d'abord les autres mouvements
    AVANT de faire l'action souhaitée
"""

def stop_before_backward(selectedCar):
    reset_wheels(selectedCar)
    try:
        appareils_connectes[selectedCar].send('\x00')  # STOP Forward
    except (OSError, AttributeError) as e :
        text_state_car.set("You are not connected !")
        print(e)

def stop_before_forward(selectedCar):
    reset_wheels(selectedCar)
    try:
        appareils_connectes[selectedCar].send('\x02')  # STOP Backward
    except (OSError, AttributeError) as e :
        text_state_car.set("You are not connected !")
        print(e)

def stop_all(selectedCar):
    reset_wheels(selectedCar)
    try:
        appareils_connectes[selectedCar].send('\x00')  # STOP Forward
        appareils_connectes[selectedCar].send('\x02')  # STOP Backward
    except (OSError, AttributeError) as e :
        text_state_car.set("You are not connected !")
        print(e)

"""
Bind des touches :
    A : Reculer et tourner à gauche
    E : Reculer et tourner à droite
    Z : Avancer en ligne droite
    S : Reculer en ligne droite
    Q : Avancer et tourner à gauche
    D : Avancer et tourner à droite
"""

###########################################################################
# Fonctions directement associées aux Listeners sur les touches assignées
def move_forward(event):
    selectedCar = choix_voitures.current()
    stop_before_forward(selectedCar)  # reset current moves
    try :
        if (varRec.get()):
            macro_rec.append(1)
        else:
            appareils_connectes[selectedCar].send('\x01')  # Avance en ligne droite
            sv.set('Forward\n' + sv.get())  
    except (OSError, AttributeError) as e :
        text_state_car.set("You are not connected !")
        print(e)

def move_backward(event):
    selectedCar = choix_voitures.current()
    stop_before_backward(selectedCar)  # reset current moves
    try:
        if (varRec.get()):
            macro_rec.append(2)
        else:
            appareils_connectes[selectedCar].send('\x03')  # Recule en ligne droite
            sv.set('Backward\n' + sv.get())
    except (OSError, AttributeError) as e :
        text_state_car.set("You are not connected !")
        print(e)

# Fonctions de déplacements plus avancées
# Avance et tourne à gauche simultanément
def forward_to_left(event):
    selectedCar = choix_voitures.current()
    try:
        if (varRec.get()):
            macro_rec.append(3)
        else:
            appareils_connectes[selectedCar].send('\x05')  # Tourne à gauche
            appareils_connectes[selectedCar].send('\x01')  # Avance
            sv.set('Forward Left\n' + sv.get())
    except (OSError, AttributeError) as e :
        text_state_car.set("You are not connected !")
        print(e)

# Avance et tourne à droite simultanément
def forward_to_right(event):
    selectedCar = choix_voitures.current()
    try:
        if (varRec.get()):
            macro_rec.append(4)
        else:
            appareils_connectes[selectedCar].send('\x07')  # Tourne à droite
            appareils_connectes[selectedCar].send('\x01')  # Avance
            sv.set('Forward Right\n' + sv.get())
    except (OSError, AttributeError) as e :
        text_state_car.set("You are not connected !")
        print(e)

# Recule et tourne à gauche simultanément
def backward_to_left(event):
    selectedCar = choix_voitures.current()
    try:
        if (varRec.get()):
            macro_rec.append(5)
        else:
            appareils_connectes[selectedCar].send('\x05')  # Tourne à gauche
            appareils_connectes[selectedCar].send('\x03')  # Recule
            sv.set('Backward Left\n' + sv.get())
    except (OSError, AttributeError) as e :
        text_state_car.set("You are not connected !")
        print(e)
        
# Recule et tourne à droite simultanément       
def backward_to_right(event):
    selectedCar = choix_voitures.current()
    try:
        if (varRec.get()):
            macro_rec.append(6)
        else:
            appareils_connectes[selectedCar].send('\x07')  # Tourne à droite
            appareils_connectes[selectedCar].send('\x03')  # Recule
            sv.set('Backward Right\n' + sv.get())
    except (OSError, AttributeError) as e :
        text_state_car.set("You are not connected !")
        print(e)

###########################################################################
# Fonctions de macro prédéfinies

# Macro 1 - Demi-tour gauche
def m1(event):
    forward_to_left(event)
    time.sleep(1)
    backward_to_right(event)
    time.sleep(1)
    forward_to_left(event)

# Macro 2 - Demi-tour droite
def m2(event):
    forward_to_right(event)
    time.sleep(1)
    backward_to_left(event)
    time.sleep(1)
    forward_to_right(event)

# Macro 3 - Cercle dans le sens des aiguilles d'une montre
def m3(event):
    forward_to_right(event)
    time.sleep(0.5)
    forward_to_right(event)
    time.sleep(0.5)
    forward_to_right(event)
    time.sleep(0.5)
    forward_to_right(event)
    time.sleep(0.5)
    forward_to_right(event)

# Macro 4 - Cercle dans le sens inverse des aiguilles d'une montre
def m4(event):
    forward_to_left(event)
    time.sleep(0.5)
    forward_to_left(event)
    time.sleep(0.5)
    forward_to_left(event)
    time.sleep(0.5)
    forward_to_left(event)
    time.sleep(0.5)
    forward_to_left(event)

# Macro 5 - Rangement en creneau
def m5(event):
    move_forward(event)
    time.sleep(0.5)
    backward_to_right(event)
    time.sleep(1)
    backward_to_right(event)
    time.sleep(1)
    backward_to_left(event)
    time.sleep(0.1)

# Macro 6 - Rangement en épis avant
def m6(event):
    forward_to_left(event)
    time.sleep(1)
    move_backward(event)

# Macro 7 - Rangement en épis arriere
def m7(event):
    backward_to_left(event)
    time.sleep(1)
    move_forward(event)

# Macro 8 - Slalom
def m8(event):
    forward_to_right(event)
    time.sleep(0.7)
    forward_to_left(event)
    time.sleep(0.7)
    forward_to_right(event)
    time.sleep(0.7)
    forward_to_left(event)
    time.sleep(0.7)
    forward_to_right(event)

###########################################################################
# Fonction d'enregistrement

def write_rec():
    global macro_rec
    print("oui")
    if (varRec.get()):
        print("BEGIN : REC")
    else:
        print("END : REC")
        print(macro_rec)
        macro_rec = []

def read_rec(event,macro):
    for c in macro:
        if (c==1):  
            move_forward(event)
        elif (c==2):
            move_backward(event)
        elif (c==3):
            forward_to_left(event)
        elif (c==4):
            forward_to_right(event)
        elif (c==5):
            backward_to_left(event)
        elif (c==6):  
            backward_to_right(event)
        time.sleep(1)        


###########################################################################
# Tkinter
root = Tk()
root.title('Control Interface')
largeur = 650
hauteur = 500
root.geometry('' + str(largeur) + 'x' + str(hauteur))
root.maxsize(largeur, hauteur)
root.resizable(width=False, height=False)

# Debut top--------------------------------------------------------------------------------

# Top application
top = Label(root, bg="gray7")
top.pack(anchor="n",fill=X)

# Label pour logos
logos = Label(top, bg="gray7")
logos.pack(anchor="w",side=LEFT,fill=Y)

# Label pour neocampus et bluetooth logo
blue_neo = Label(logos, bg="gray7")
blue_neo.pack(anchor="e",side=TOP,fill=X)

# Affichage Logos
photo_bluetooth = PhotoImage(file = "Vroum2.png")
logo_bluetooth = Label(blue_neo, image= photo_bluetooth, bg="gray7")
logo_bluetooth.pack(side=LEFT)

photo_neo = PhotoImage(file = "neocampus.png")
logo_neo = Label(blue_neo, image= photo_neo, bg="gray7")
logo_neo.pack(side=LEFT)

photo_ps = PhotoImage(file = "paulsab.png")
logo_ps = Label(logos, image= photo_ps, bg="gray7")
logo_ps.pack(anchor="nw",side=LEFT,padx=10)

# Frame pour liste de commandes
frame_liste_commandes = Frame(top, height = 100, width=120, background="steel blue")
frame_liste_commandes.pack(anchor="ne",side= RIGHT, padx = 20, pady=20)

# Affichage liste commandes
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

# Fin top--------------------------------------------------------------------------------

# Debut mid--------------------------------------------------------------------------------

# Mid application
mid = Label(root, height = 200, width=600, background="gray7")
mid.pack(anchor="center", fill=X)

# Variable texte pour l'historique
sv = StringVar()

# Variable entiere pour l'enregistrement
varRec = IntVar()

# Historique des commandes
historique = Label(mid, textvariable=sv, font='Helvetica 12 ', fg='red', bg='steel blue',anchor=NW, width=20, height=15)
#scroll = Scrollbar(historique, orient='vertical')
#scroll.pack(anchor="e",side=RIGHT)
historique.pack(anchor="w",padx=20, side= LEFT)

# Frame pour stocker les flèches
frame_fleches = Frame(mid, height=150, width=200, background="gray7")
frame_fleches.pack(anchor="center", side=LEFT, padx=60)

# Frame pour stocker fleches marche avant
fleches_avance = Frame(frame_fleches, height=150, width=100)
fleches_avance.pack(anchor="center",side=TOP)

# Frame pour stocker fleches marche arriere
fleches_arriere = Frame(frame_fleches, height=150, width=100)
fleches_arriere.pack(anchor="center",side=TOP)

# Frame pour stocker les boutons annexes
frame_annexes = Frame(frame_fleches, height=150, width=100)
frame_annexes.pack(anchor="center",side=TOP)

# Boutons de contrôle de l'interface graphique
fleche_gauche = Button(fleches_avance, text='←', command = lambda: forward_to_left(''), width=3 , height=3)
fleche_gauche.pack(side=LEFT)
fleche_haut = Button(fleches_avance, text='↑', command = lambda: move_forward(''), width=3 , height=3)
fleche_haut.pack(side=LEFT)
fleche_droite = Button(fleches_avance, text='→', command = lambda: forward_to_right(''), width=3 , height=3)
fleche_droite.pack(side=LEFT)
fleche_back_gauche = Button(fleches_arriere, text='←|', command = lambda: backward_to_left(''), width=3 , height=3)
fleche_back_gauche.pack(side=LEFT)
fleche_bas = Button(fleches_arriere, text='↓', command = lambda: move_backward(''), width=3 , height=3)
fleche_bas.pack(side=LEFT)
fleche_back_droite = Button(fleches_arriere, text='|→', command = lambda: backward_to_right(''), width=3 , height=3)
fleche_back_droite.pack(side=LEFT)
btn_stop = Button(frame_annexes, text='STOP', command = lambda: stop_all(''), width=3 , height=3)
btn_stop.pack(side=LEFT)
btn_rec = Checkbutton(frame_annexes, variable=varRec, text='REC', command = write_rec, width=3 , height=3, indicatoron=0)
btn_rec.pack(side=LEFT)

# Frame pour stocker les boutons de démos
frame_demos=Frame(mid,height = 150, width=180, background="steel blue")
frame_demos.pack(anchor="e",side = LEFT, padx=20, fill=BOTH)

# Boutons pour lancer des démos (circuits)
liste_macro = Label(frame_demos, bg='navy',fg="white", text="     Liste de Macro      ", font='Helvetica 12 bold')
liste_macro.pack(anchor="n")
macro_1 = Label(frame_demos, text="Macro 1", fg="black", font='Helvetica 12 ', background="steel blue")
macro_1.pack()
macro_1.bind("<Button-1>",m1)
macro_2 = Label(frame_demos, text="Macro 2", fg="black", font='Helvetica 12 ', background="steel blue")
macro_2.pack()
macro_2.bind("<Button-1>",m2)
macro_3 = Label(frame_demos, text="Macro 3", fg="black", font='Helvetica 12 ', background="steel blue")
macro_3.pack()
macro_3.bind("<Button-1>",m3)
macro_4 = Label(frame_demos, text="Macro 4", fg="black", font='Helvetica 12 ', background="steel blue")
macro_4.pack()
macro_4.bind("<Button-1>",m4)
macro_5 = Label(frame_demos, text="Macro 5", fg="black", font='Helvetica 12 ', background="steel blue")
macro_5.pack()
macro_5.bind("<Button-1>",m5)
macro_6 = Label(frame_demos, text="Macro 6", fg="black", font='Helvetica 12 ', background="steel blue")
macro_6.pack()
macro_6.bind("<Button-1>",m6)
macro_7 = Label(frame_demos, text="Macro 7", fg="black", font='Helvetica 12 ', background="steel blue")
macro_7.pack()
macro_7.bind("<Button-1>",m7)
macro_8 = Label(frame_demos, text="Macro 8", fg="black", font='Helvetica 12 ', background="steel blue")
macro_8.pack()
macro_8.bind("<Button-1>",m8)

# Fin top--------------------------------------------------------------------------------

# Debut bot--------------------------------------------------------------------------------

# Bot application
bot = Label(root, height = 200, width=600, background="gray7")
bot.pack(anchor="s", fill=X)

# Variable texte pour état voiture
text_state_car = StringVar()
text_state_car.set("Etat de la voiture")
lb_connect = LabelFrame(root, bg='green')
lb_connect.pack(anchor="w",side = LEFT, padx=20,pady=10)

# Label état voiture connectée
state_car=Label(bot,height = 30,textvariable=text_state_car, width=40,fg='red', bg='steel blue',anchor=W)
state_car.pack(anchor="w",side = LEFT, padx=20,pady=10)

# Frame pour stocker liste deroulante des voitures et bouton login
frame_connexion=Frame(bot,height = 150, width=250, background="steel blue")
frame_connexion.pack(anchor="e",side = RIGHT, padx=20,pady=10)

# Liste deroulante pour le choix de la voiture à connecter
choix_voitures = ttk.Combobox(frame_connexion, values=[],
                              state="disabled")  # readonly au départ car aucune voiture n'a été détéctée pour le moment
choix_voitures.pack(side=LEFT,padx=5)

# Connexion à une voiture une fois séléctionnée
btn_connect = Button(frame_connexion, text='Connect', command = lambda: f_connect(), state=DISABLED)
btn_connect.pack(side=RIGHT, padx=5)

# Scan des appareils "beewi" bluetooth proches
scan = Button(frame_connexion, text='BT Scan', command = lambda: f_scan())
scan.pack(side=RIGHT, padx=5)

# Fin bot--------------------------------------------------------------------------------

# Listeners des flèches au clavier
root.bind('<a>', forward_to_left)
root.bind('<e>', forward_to_right)
root.bind('<q>', backward_to_left)
root.bind('<d>', backward_to_right)
root.bind('<z>', move_forward)
root.bind('<s>', move_backward)
root.bind('<space>', stop_all)
 
# Affichage de l'interface graphique
mainloop()

###########################################################################
