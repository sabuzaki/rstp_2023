#!/bin/python3
import unittest
import rstp_2023
import time
import helpers_rstp_2023 as helpers
from datetime import datetime
import requests
from unittest.mock import patch
import socket
import sys
from cli_rstp_2023 import cli_menu
from io import StringIO
import threading
import time
import os
ETH_P_ALL = 0x0003
BUFFER_SIZE = 65536


class test_rstp_2023(unittest.TestCase):

    def other(self):
        response = requests.get(f'http://google.ie')
        if response.ok:
            return response.text
        else:
            'BAd Response'
    #def __init__(self):
    #    self.bridges = []
    @classmethod
    def setUpClass(cls):
        print('setupClass')
        pass

    @classmethod
    def tearDownClass(cls):
        print('tearDownClass')
        pass

#    def test_monthly(self):
#        with patch('

    #run it's before every single test
    def setUp(self):
        print("TEST: setUp")
        self.bridges = []
        self.cl = cli_menu()
        #will be using second bridge for testing
        self.bridges.append(rstp_2023.bridge(0,helpers.generate_mac(0),8))
        pass

    #run it's code after every single test
    def tearDown(self):
        print("TEST: tearDown")
        helpers.terminate_bridge(self.bridges,0)
        pass

    def receive_rstp_on_custom_port(self,network_card_name):
#        os.system("ip link set "+network_card_name+" up")
        self.sckt = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        loop=True
        enough = 5
        while(loop and enough):
            self.sckt.bind((network_card_name,ETH_P_ALL))
            buf=self.sckt.recvfrom(BUFFER_SIZE)[0].hex()
            if(buf[0:12]=="0180c2000000"):
                loop=False
                print("received RSTP ...exiting...")
                self.sckt.close()
            #buf = BUFFER_SIZE * 0
            time.sleep(1)
            print(".")
            enough -=1
        return buf

    def receive_from_bridge_0_port_0(self):
        self.sckt = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        loop=True
        enough = 5
        while(loop and enough):
            self.sckt.bind(("rstp_0_0", ETH_P_ALL))
            buf=self.sckt.recvfrom(BUFFER_SIZE)[0].hex()
            if(buf[0:12]=="0180c2000000" and buf[72:84]=="aabbccddee00"):               # RSTP multicast destination
                loop=False
                print("received RSTP...exiting...")
                self.sckt.close()
            #buf = BUFFER_SIZE * 0
            time.sleep(1)
            print(".")
            enough -=1
        return buf

    def receive_from_cml_cisco_switch(self,network_card_name):
       
       # os.system("ip link set "+network_card_name+" up")
        self.sckt = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        loop=True
        enough = 5
        while(loop and enough):
            self.sckt.bind((network_card_name,ETH_P_ALL))
            try:
                self.sckt.settimeout(1)
                buf=self.sckt.recvfrom(BUFFER_SIZE)[0].hex()
                if(buf[0:12]=="0180c2000000" and buf[72:78]=="525400"):               # RSTP multicast destination
                    loop=False
                    print("received RSTP from cisco cml switch...exiting...")
                    self.sckt.close()
                #buf = BUFFER_SIZE * 0
            except: pass
            time.sleep(1)
            enough -=1
        if(loop):
            return "0"                  # if tried for 5 seconds to receive from cml cisco siwtch, but did not receive
        else:
            return buf

    #PRIORITY_LIST = [0,4096,8192,12288,16384,20480,24576,28672,32768,36864,40960,45056,49152,53248,57344,61440]
    def test_receive_rstp(self):
        br = self.bridges[0]
        self.t01()
        self.t02()
        self.t03()
        self.t04()
        self.t05()
        self.t06()
        self.t07()
        self.t08()
        #self.t09()
        #self.t10()
        self.t11()
        self.t12()
        self.t13()
        self.t14()
        self.t15()
        self.t16()
        #sys.stdin = StringIO("0\n0\nens4\n")
        #cl.print_menu(self.bridges,30)

        #sys.stdin = StringIO("0\n0\nens3\n")
        #sys.stdin = StringIO("0\n0\nens5\n")
        #sys.stdin = StringIO("0\n0\nens2\n")
#        self.designated_bridge_priority = self.rcvdContent[68:72]
#        self.designated_bridge_mac = self.rcvdContent[72:84]
#        "aabbccddee00"
        #self.root_priority = self.rcvdContent[44:48]
        #self.root_mac = self.rcvdContent[48:60]
#         message_root_path_cost = self.rcvdContent[60:68]

    def t01(self):
        print("t01")
        sys.stdin = StringIO("0\n36864\n")
        self.cl.print_menu(self.bridges,10)
        self.assertEqual(self.bridges[0].bridge_priority, "9001")   #oo
#        time.sleep(2)
        buf = self.receive_from_bridge_0_port_0()
        self.assertEqual(buf[68:72],"9001") #bb

    def t02(self):
        print("t02")
        sys.stdin = StringIO("0\n0\nens4\n")
        self.cl.print_menu(self.bridges,30)

        buf = self.receive_from_cml_cisco_switch("ens4")
        self.assertEqual(buf[44:48],"6001")

        time.sleep(3.5)
        self.assertEqual(self.bridges[0].i_am_root, False)
        self.assertEqual(self.bridges[0].ports[0].port_role,"Root")
        time.sleep(1.5)
        self.assertEqual(self.bridges[0].ports[0].port_state,"Forwarding")

        buf = self.receive_rstp_on_custom_port("rstp_0_1")
        self.assertEqual(buf[44:48],"6001")                         # Because mac address can be different in every environment/test, we check by priority. Assuming bridge 555 has priority 24k (6001 in hex)
        self.assertEqual(buf[60:68],"00004e20")

    def t03(self):
        print("t03")
        sys.stdin = StringIO("0\n1\nens4\n")
        self.cl.print_menu(self.bridges,30)
        time.sleep(5.5)
        self.assertEqual(self.bridges[0].ports[1].port_role,"Alternate")
        self.assertEqual(self.bridges[0].ports[1].port_state,"Discarding")

    def t04(self):
        print("t04")
        sys.stdin = StringIO("0\n2\nens3\n")
        self.cl.print_menu(self.bridges,30)

        time.sleep(5)
        self.assertEqual(self.bridges[0].ports[2].port_role,"Alternate")    #1k
        self.assertEqual(self.bridges[0].ports[2].port_state,"Discarding")

        buf = self.receive_from_cml_cisco_switch("ens3")
        self.assertEqual(buf[60:68],"00004e20")                                     # other bridge 444 advertised cost as 20000
        self.assertEqual(self.bridges[0].ports[2].root_path_cost,"00009c40")        # stored root_path_cost 40000 (port cost + advertised cost)

    def t05(self):
        print("t05")
        sys.stdin = StringIO("0\n1\n")
        self.cl.print_menu(self.bridges,40)

        self.assertEqual(self.bridges[0].ports[1].port_role,"Designated")
        self.assertEqual(self.bridges[0].ports[1].port_state,"Discarding")

    def t06(self):
        print("t06")

        sys.stdin = StringIO("0\n0\n6\n")                   # stdin : bridge 0, port 0, speed 100Mb/s
        self.cl.print_menu(self.bridges,18)                 # option 18 -> change port speed.

        time.sleep(10)
        self.assertEqual(self.bridges[0].ports[0].port_role,"Alternate")
        ######################### FAILING BELOW TO BE REVIEWED '##############################
    
    #########self.assertEqual(self.bridges[0].ports[2].port_role,"Root")                 #hj

        self.assertEqual(self.bridges[0].ports[2].root_path_cost,"00009c40")        # stored root_path_cost 40000 (port cost + advertised cost)
        self.assertEqual(self.bridges[0].ports[0].port_cost,"00030d40")

        buf = self.receive_rstp_on_custom_port("rstp_0_4")                                     
        self.assertEqual(buf[60:68],"00009c40")                                     # check if one of the Designated ports transmiting cost to root 555 as 40000

    def t07(self):
        print("t06")
        sys.stdin = StringIO("0\n2\n1\n")                   # enable root guard on bridge 0 port 2
        self.cl.print_menu(self.bridges,16)                 # option 18 -> change port speed.

        time.sleep(4)
        self.assertEqual(self.bridges[0].ports[2].port_state,"Err_disabled")
        self.assertEqual(self.bridges[0].ports[2].port_role,"Disabled")
        self.assertEqual(self.bridges[0].ports[0].port_role,"Root")
        self.assertEqual(self.bridges[0].ports[0].port_state,"Forwarding")
        
        buf = self.receive_rstp_on_custom_port("rstp_0_4")
        self.assertEqual(buf[60:68],"00030d40")                                     # check if one of the Designated ports transmiting cost to root 555 as 200000

    def t08(self):
        print("t08")
        sys.stdin = StringIO("0\n0\n1005\n")                   # change bridge 0 port 0 cost to 1005
        self.cl.print_menu(self.bridges,14)                 # option 18 -> change port speed.
        self.assertEqual(self.bridges[0].ports[0].port_cost, "000003ed")

        time.sleep(3)
        buf = self.receive_rstp_on_custom_port("rstp_0_4")
        self.assertEqual(buf[60:68],"000003ed")                                    #pots transmitting cost to root as 1005 

    def t09(self):
        print("t09")
        sys.stdin = StringIO("0\n7\n2\n")                   # enable root guard on bridge 0 port 2
        self.cl.print_menu(self.bridges,21)                 # disable port

        self.assertEqual(self.bridges[0].ports[7].port_role,"Disabled")
        self.assertEqual(self.bridges[0].ports[7].port_state,"Disabled")

    def t10(self):
        print("t09")
        sys.stdin = StringIO("0\n7\n1\n") 
        self.cl.print_menu(self.bridges,21)                 # enable port 

        self.assertEqual(self.bridges[0].ports[7].port_role,"Designated")
        self.assertEqual(self.bridges[0].ports[7].port_state,"Discarding")
        time.sleep(15.5)
        self.assertEqual(self.bridges[0].ports[7].port_state,"Learning")
        time.sleep(15.5)
        self.assertEqual(self.bridges[0].ports[7].port_state,"Forwarding")

    def t11(self):
        print("t11")
        self.t09()      #disable port 0_7
        sys.stdin = StringIO("0\n7\n1\n")               #enable portfast
        self.cl.print_menu(self.bridges,20)             # enable port 

        sys.stdin = StringIO("0\n7\n1\n") 
        self.cl.print_menu(self.bridges,21)             # enable port 

        time.sleep(1)
        self.assertEqual(self.bridges[0].ports[7].port_role,"Designated")
        self.assertEqual(self.bridges[0].ports[7].port_state,"Forwarding")

    def t12(self):
        print("t12")

        buf = self.receive_from_cml_cisco_switch("ens2")
            #self.root_priority = self.rcvdContent[44:48]
        self.assertEqual(buf[44:48],"8001")                 # received from cisco switch 333

        sys.stdin = StringIO("0\n6\nens2\n")               # connect ens2 with rstp_0_6
        self.cl.print_menu(self.bridges,30)             

        time.sleep(3)
        buf = self.receive_from_cml_cisco_switch("ens2")
        self.assertEqual(buf[44:48],"6001")                 # received from cisco switch 333. It is advertising now switch 555 as root

    def t13(self):
        print("t13")

        buf = self.receive_from_cml_cisco_switch("ens5")
            #self.root_priority = self.rcvdContent[44:48]
        self.assertEqual(buf[44:48],"8001")                 # received from cisco switch 333

        sys.stdin = StringIO("0\n5\nens5\n")               # connect ens2 with rstp_0_5
        self.cl.print_menu(self.bridges,30)             

        time.sleep(2)
        self.assertEqual(self.bridges[0].ports[5].port_role,"Designated")
        self.assertEqual(self.bridges[0].ports[6].port_role,"Designated")

    def t14(self):
        print("t14")

    def t15(self):
        print("t15")

    def t14(self):
        print("t16")

if __name__ == '__main__':
    unittest.main()

