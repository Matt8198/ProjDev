#!/usr/bin/env python3
#
# Theo Riviere  jun.19  initial release
#



################################################################################
# Import zone
#
import os
import sys
import time

from bluetooth import *



################################################################################
# Global variables
#
_detected = False
_macaddr = None
_connected = False



################################################################################
# Functions
#



################################################################################
# Main
#

# bluetooth scan
print("Scan for BeeWi mini cooper ...")
while( _detected is not True ):
    print("Start scanning ...")
    res = discover_devices(lookup_names=True)
    # parse results
    for _mac,_name in res:
        if( _name.lower().startswith("beewi mini cooper") ):
            print("\tBeeWi detected :)")
            time.sleep(1)
            _macaddr = _mac
            _detected = True
    if( _detected is not False ):
        break
    # restart scanning
    print("not detected ... sleeping a bit before restarting scan ...")
    time.sleep(3)

# Create the client socket
print("\nConnect to vehicule ...")
client_socket = BluetoothSocket( RFCOMM )

res = client_socket.connect((_macaddr, 1))
print("Connection successful :)")
#client_socket.send("Hello World")

time.sleep(1)
print ("\nNow you can give orders with the touch :")
time.sleep(2)
print("\n\t\t- ← : Go Left")
time.sleep(1)
print("\t\t- → : Go Right")
time.sleep(1)
print("\t\t- ↑ : Go Forward")
time.sleep(1)
print("\t\t- ↓ : Go Backward\n")
time.sleep(1)

print("But first and foremost a little test session :\n")
time.sleep(2.5)

client_socket.send( '\x05' )
print("\t\t~ Left")
time.sleep(0.5)
client_socket.send( '\x04' )
print("\t\t~ Nothing")
time.sleep(0.5)
client_socket.send( '\x07' )
print("\t\t~ Right")
time.sleep(0.5)
client_socket.send( '\x06' )
print("\t\t~ Nothing")
time.sleep(0.5)
client_socket.send( '\x01' )
print("\t\t~ Forward")
time.sleep(0.5)
client_socket.send( '\x00' )
print("\t\t~ Nothing")
time.sleep(1)
client_socket.send( '\x03' )
print("\t\t~ Backward")
time.sleep(0.5)
client_socket.send( '\x02' )
print("\t\t~ Nothing")
time.sleep(0.5)

client_socket.close()
print("\nThe test is finished")
time.sleep(0.5)
print("Now you can pilot the car\n")

