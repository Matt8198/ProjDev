# coding: utf-8
 
from tkinter import *

main = Tk()

# TODO : Lier les touches de l'interface avec les ordres pour commander la voiture
def leftKey(event):
    #client_socket.send( '\x05' )
    print("Left key pressed")

def rightKey(event):
    #client_socket.send( '\x07' )
    print("Right key pressed")

def upperKey(event):
    #client_socket.send( '\x01' )
    print("Upper key pressed")

def downKey(event):
    #client_socket.send( '\x03' )
    print("Down key pressed")    

frame = Frame(main, width=800, height=800)
# listeners
main.bind('<Left>', leftKey)
main.bind('<Right>', rightKey)
main.bind('<Up>', upperKey)
main.bind('<Down>', downKey)

# affichage de l'interface
frame.pack()
main.mainloop()
