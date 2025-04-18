#!/bin/python3

# port_name is the same as ethernet/bridge name in linux OS
# aaaaaa

#ETH_P_ALL = 0x0003
import socket
import time
import sys
import threading
import secrets
#from datetime import datetime
import os
from cli_rstp_2023 import cli_menu
#import cli_rstp_2023
import helpers_rstp_2023 as helpers
#from helpers_rstp_2023 import logger
from datetime import datetime
from bridge_rstp_2023 import bridge
import argparse
import threading

class update_rstp_graph_jpg(threading.Thread):
    def __init__(self,bridges):
        self.bridges = bridges
        threading.Thread.__init__(self)

    def run(self):
        while(1):
           helpers.generate_graphviz(self.bridges,True)             # True means that it is generating rstp_graph.jpg instead of output onto the menu
           time.sleep(2)


# Ports are the same as ethernet/bridge cards in this application
#ports = []
bridges = [] #[""]#,"","",""]

#return "0180c20000005254aa1caabb0029424203000000000010015254aa1caabb0000000010015254aa1caabb80030000140002000f00000000"

#apt install python3-pip
#apt install python3-dev graphviz libgraphviz-dev pkg-config 
#apt install python3-tk
#apt install python3-pil.imagetk
#pip3 install graphviz
#pip3 install netifaces
#pip3 install numpy
#pip3 install tabulate
#pip3 install pygraphviz

if __name__ == "__main__":

#    n = len(sys.argv)
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', type=int, help='Enter amount of bridge to create. Max: 16. Default 5')
    parser.add_argument('-p', type=int, help='Enter amount of ports per bridge to create. Max: 24. Default: 4')
    args = parser.parse_args()
    bridge_count = 3
    port_count = 8
    if(args.b is not None):
        if(args.b>16 or args.b <= 0):
            print("Error. Bridge range: 1-16. Default is 5.")
            quit()
        else:
            bridge_count = args.b
    if(args.p is not None):
        if(args.p>24 or args.p <=  0):
            print("Error. Port range: 1-24. Default is 8.")
            quit()
        else:
            port_count = args.p
    p = 0
    cl = cli_menu()
    for i in range(0,bridge_count):
        bridges.append(bridge(i,helpers.generate_mac(i),port_count))    # temporarily
#        bridges.append(bridge(i,helpers.generate_mac(),port_count))    # original

    helpers.create_hub(0)               # one hub is enough for training purpose
    #val = os.fork()
    #if(val==0):                 # I'm a child process. This will update rstp_graph.jpg every 2 seconds.
    #   update_rstp_graph_jpg(bridges).start()
    #   exit()
       #self.graph_thread.start()

    #cli_rstp_2023.show_menu(bridges)
    cl.show_menu(bridges)
    while(1):
       menu_var = helpers.get_number("Enter selection number (0 to show menu): 1 - ", 99)
       #cli_rstp_2023.print_menu(bridges,menu_var)
       cl.print_menu(bridges,menu_var)
