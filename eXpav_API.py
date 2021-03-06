import os
import sys
import time
from copy import deepcopy
from tkinter import *
import tkinter.ttk as ttk 
from BluetoothClass import * 

# Initialise n emplacements pour des sockets Bluetooth
appareils_connectes = [None] * 2  # 3 Voitures simultannées au maximum
appareils_connectes_parallele=[]
macro_rec = []
ordre=[]
ordre_rec = []
drapeau_multicar = False
#Initialise les noms des appreils connectés
app_1 = ""
app_2 = ""
app_3 = ""
apps=[app_1, app_2, app_3]

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
appareilsDispo = []      # Liste des appareils proches
def f_scan():
    text_state_car.set('Start scanning')
    appareilsDetectes = discover_devices(lookup_names=True, duration=2)
    print("appareilsDetectes =", appareilsDetectes)

    if appareilsDispo == [] :
        #La liste des appareils PROCHES
        for _mac, _name in appareilsDetectes:
            # Filtre seulement les appareils "beewi"
            if "beewi" in _name.lower():
                print(_mac, " ", _name)
                appareilsDispo.append((_mac, _name))
        print("appareilsDispo =", appareilsDispo)
        for newMac, newName in appareilsDispo:
            # On a une nouvelle voiture Beewi
            if ("beewi" in newName.lower()):
                # Ajoute un nouveau véhicule à la fin de la liste de choix
                choix_voitures['values'] = (*choix_voitures['values'], newName)
    else :
        macDispo = [x[0] for x in appareilsDispo]
        # print("maaac",macDispo)
        # Met à jour la liste des véhicules disponibles
        for newMac, newName in appareilsDetectes:
            print(newMac,newName)
            # On a une nouvelle voiture Beewi
            if (newMac not in macDispo) and ("beewi" in newName.lower()):
                # Ajoute un nouveau véhicule à la fin de la liste de choix
                choix_voitures['values'] = (*choix_voitures['values'], newName)

    # Maintenant on peut selectionner une voiture :
    choix_voitures['state'] = "enabled"
    btn_connect['state'] = NORMAL

# Bluetooth connection
def f_connect():
    car = []
    selectedCar = choix_voitures.current()
    # choix_voitures['state'] = "disabled"
    # Assure qu'on ait choisi une voiture parmi les choix disponibles
    if selectedCar != -1 : 
        try :
            car = appareilsDispo[selectedCar]
            # Connexion à la voiture
            macaddr = car[0]
        except IndexError:  # outofbounds
            text_state_car.set('Please enable Bluetooth on your laptop !')

        if (car != []):
             # Enregistre la socket associée à la voiture connectée
            new_sock = Bluetooth()
            try :
                new_sock.connect(macaddr)
                appareils_connectes[selectedCar] = new_sock  # passe le numéro de la voiture (indice de la liste de choix)
            except OSError:
                # Gère une erreur de connexion, si on désactive le bluetooth après le scan
                print("Connection ERROR ! Device is not ON/available")
    print("Les appareils connectes :",appareils_connectes)

#Affichage appareils connectés
def devices_connected(car):
    for i in range (len(apps)):
        if(apps[i] == ""):
            apps[i] = car
    app_connect_1.pack_forget()
    app_connect_2.pack_forget()
    app_connect_3.pack_forget()
    app_connect_1.pack(anchor="n")
    app_connect_2.pack(anchor="n")
    app_connect_3.pack(anchor="n")

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

def stop_all(event):
    selectedCar = choix_voitures.current()
    try:
        appareils_connectes[selectedCar].send('\x00')  # STOP Forward
        appareils_connectes[selectedCar].send('\x02')  # STOP Backward
    except (OSError, AttributeError) as e :
        text_state_car.set("You are not connected !")
        print(e)
    reset_wheels(selectedCar)

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
        elif (ordreRec.get()):
            ordre_rec.append("avancer")
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
        elif (ordreRec.get()):
            ordre_rec.append("reculer")
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
        elif (ordreRec.get()):
            ordre_rec.append("avancerGauche")
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
        elif (ordreRec.get()):
            ordre_rec.append("AvancerDroite")
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
        elif (ordreRec.get()):
            ordre_rec.append("reculerGauche")
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
        elif (ordreRec.get()):
            ordre_rec.append("reculerDroite")
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

def write_rec_ordre():
    global ordre_rec
    if (ordreRec.get()):
        print("BEGIN ORDRE : REC")
    else:
        print("END ORDRE: REC")
        print(ordre_rec)
        ordre.append(ordre_rec)
        ordre_rec = []

###########################################################################
# Fonction pour connecté toutes les beewi disponible
def connexion_parallele():
    global appareils_connectes_parallele
    appareils_connectes_parallele=[]
    appareilsDispo = []
    appareilsDetectes = discover_devices(lookup_names=True, duration=2)
    print("appareilsDetectes =", appareilsDetectes)

    #On récupère toutes les Beewi dispo
    if appareilsDispo == [] :
        #La liste des appareils PROCHES
        for _mac, _name in appareilsDetectes:
            # Filtre seulement les appareils "beewi"
            if "beewi" in _name.lower():
                print(_mac, " ", _name)
                appareilsDispo.append((_mac, _name))
                
    print("dispo",appareilsDispo)

    #On connecte toutes les Beewi
    for i in range(len(appareilsDispo)):
        selectedCar=i
        if selectedCar != -1 : 
            try :
                car = appareilsDispo[selectedCar]
                # Connexion à la voiture
                macaddr = car[0]
            except IndexError:  # outofbounds
                print('Please enable Bluetooth on your laptop !')

            if (car != []):
                # Enregistre la socket associée à la voiture connectée
                new_sock = Bluetooth()
                try :
                    new_sock.connect(macaddr)
                    print(macaddr+' est connecté')
                    appareils_connectes_parallele.append(new_sock)  # passe le numéro de la voiture (indice de la liste de choix)
                except OSError:
                    # Gère une erreur de connexion, si on désactive le bluetooth après le scan
                    print("Connection ERROR ! Device is not ON/available")
                

    print("Appareils Connectés",appareils_connectes_parallele)
    print("Il vous faut faire "+ str(len(appareils_connectes_parallele)) + " listes d'ordres")
##################################################################

##################################################################
#Fonction pour appeler les ordres que l'on a crée.
def lancement_parallele():
    global ordre
    global appareils_connectes_parallele

    #Prendre la liste la plus grande comme repere
    if len(ordre)==len(appareils_connectes_parallele):
        maxi = 0
        for i in (ordre):
            if len(i)>maxi:
                maxi = len(i)
        
        temps = temps_label.get()
        
        #On boucle sur le nombre d'ordre maximal sur une liste
        for o in range(maxi):
            timeout_start = time.time()
            #On met une contrainte de temps
            while time.time() < timeout_start + float(temps):
                #On fait l'ordre demandés pour toutes les voitures
                for i in range(len(appareils_connectes_parallele)):
                    if o <= len(ordre[i])-1 and appareils_connectes_parallele[i]!=None:
                        appareils_connectes_parallele[i].send('\x00')  
                        appareils_connectes_parallele[i].send('\x02') 
                        if ordre[i][o] == "avancer":
                            appareils_connectes_parallele[i].send("\x01")
                        elif ordre[i][o] == "reculer":
                            appareils_connectes_parallele[i].send("\x03")
                        elif ordre[i][o] == "avancerDroite":
                            appareils_connectes_parallele[i].send('\x07')  
                            appareils_connectes_parallele[i].send("\x01")
                        elif ordre[i][o] == "avancerGauche":
                            appareils_connectes_parallele[i].send('\x05')  
                            appareils_connectes_parallele[i].send("\x01")
                        elif ordre[i][o] == "reculerDroite":
                            appareils_connectes_parallele[i].send('\x07')  
                            appareils_connectes_parallele[i].send("\x03")
                        elif ordre[i][o] == "reculerGauche":
                            appareils_connectes_parallele[i].send('\x05') 
                            appareils_connectes_parallele[i].send("\x03")
                        time.sleep(0.1)
        ordre=[]
    else:
        print("Problème, nous avons pas autant de liste d'ordres que de voitures. Il vous en faut "+ str(len(appareils_connectes_parallele))+", vous en avez "+str(len(ordre)))

###########################################################################
# Tkinter
root = Tk()
root.title('Control Interface')
largeur = 900
hauteur = 550
root.geometry('' + str(largeur) + 'x' + str(hauteur))
#root.maxsize(largeur, hauteur)
#root.resizable(width=False, height=False)

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

# Variable entiere pour l'enregistrement d'ordre en simultanées simultanées
ordreRec=IntVar()

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

# Frame pour les commandes en parallèle
frame_parallele = Frame(frame_fleches, height=150, width=100)
frame_parallele.pack(anchor="center",side=TOP)

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

# Boutons pour les ordres en parallèle
btn_multicar = Button(frame_parallele, text='Connexion Parallele', command=connexion_parallele, height=3).pack(side=LEFT)
btn_rec_ordre = Checkbutton(frame_parallele, variable=ordreRec, text='REC Ordre', command = write_rec_ordre, height=3, indicatoron=0).pack(side=LEFT)
btn_multicar = Button(frame_parallele, text='Lancement Parallele', command=lancement_parallele, height=3).pack(side=LEFT)
indication_temps = Label(frame_parallele, text="Temps" ).pack()
temps_label = StringVar()
saisir_temps = Entry(frame_parallele, textvariable=temps_label, width=5).pack()

#Frame pour démos et appareils connectés
frame_demos_et_appareils = Frame(mid,height = 150, width=180, background="gray7")
frame_demos_et_appareils.pack(anchor="e",side = LEFT, padx=20, fill=BOTH)

#Frame pour stocker les boutons de démos
frame_demos=Frame(frame_demos_et_appareils,height = 70, width=180, background="steel blue")
frame_demos.pack(anchor="n",side=TOP, fill=X)

#Frame pour stocker la liste des appareils connectés
frame_app_co=Frame(frame_demos_et_appareils,height = 70, width=80, background="steel blue")
frame_app_co.pack(anchor="s",side=BOTTOM, fill=X)

#Titre frame_app_co
titre_app_co = Label(frame_app_co, bg='navy',fg="white", text="     Appareils Connectés      ", font='Helvetica 12 bold')
titre_app_co.pack(anchor="n")

# Boutons pour lancer des démos (circuits)
liste_macro = Label(frame_demos, bg='navy',fg="white", text="     Liste de Macro      ", font='Helvetica 12 bold')
liste_macro.pack(anchor="n",fill=X)
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

# Init fenêtre devices connected
app_connect_1 = Label(frame_app_co, text=app_1, fg="black", font='Helvetica 12 ', background="steel blue")
app_connect_1.pack(anchor="n")
app_connect_2 = Label(frame_app_co, text=app_2, fg="black", font='Helvetica 12 ', background="steel blue")
app_connect_2.pack(anchor="n")
app_connect_3 = Label(frame_app_co, text=app_3, fg="black", font='Helvetica 12 ', background="steel blue")
app_connect_3.pack(anchor="n")
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


