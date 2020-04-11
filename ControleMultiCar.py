from BluetoothClass import * 
import time 

def multicar(ordre,temps,vitesse):
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
                
    appareils_connectes = [None]*len(appareilsDispo)
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
                    appareils_connectes[selectedCar] = new_sock  # passe le numéro de la voiture (indice de la liste de choix)
                except OSError:
                    # Gère une erreur de connexion, si on désactive le bluetooth après le scan
                    print("Connection ERROR ! Device is not ON/available")
                

    print("Appareils Connectés",appareils_connectes)

    #Prendre la liste la plus grande comme repere
    maxi = 0
    for i in (ordre):
        if len(i)>maxi:
            maxi = len(i)
    
    #On boucle sur le nombre d'ordre maximal sur une liste
    for o in range(maxi):
        timeout_start = time.time()
        #On met une contrainte de temps
        while time.time() < timeout_start + temps:
            #On fait l'ordre demandés pour toutes les voitures
            for i in range(len(appareils_connectes)):
                if o <= len(ordre[i])-1 and appareils_connectes[i]!=None:
                    appareils_connectes[i].send('\x00')  
                    appareils_connectes[i].send('\x02') 
                    if ordre[i][o] == "avancer":
                        appareils_connectes[i].send("\x01")
                        time.sleep(0.1)
                    elif ordre[i][o] == "reculer":
                        appareils_connectes[i].send("\x03")
                        time.sleep(0.1)
                    elif ordre[i][o] == "avancerDroite":
                        appareils_connectes[i].send('\x07')  
                        appareils_connectes[i].send("\x01")
                        time.sleep(0.1)
                    elif ordre[i][o] == "avancerGauche":
                        appareils_connectes[i].send('\x05')  
                        appareils_connectes[i].send("\x01")
                        time.sleep(0.1)
                    elif ordre[i][o] == "reculerDroite":
                        appareils_connectes[i].send('\x07')  
                        appareils_connectes[i].send("\x03")
                        time.sleep(0.1)
                    elif ordre[i][o] == "reculerGauche":
                        appareils_connectes[i].send('\x05') 
                        appareils_connectes[i].send("\x03")
                        time.sleep(0.1)



###########################################################################
if __name__ == "__main__":
    multicar([["avancer","avancerDroite","reculer"],["avancerDroite","avancerGauche"]],2,5)