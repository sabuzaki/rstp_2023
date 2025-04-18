#!/bin/python3
import unittest
import rstp_2023
import time
import helpers_rstp_2023 as helpers
from datetime import datetime
import requests
from unittest.mock import patch
import socket
ETH_P_ALL = 0x0003

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
        bridges = []
        bridges.append(rstp_2023.bridge(0,helpers.generate_mac(0),4))
        #will be using second bridge for testing
#        self.bridges.append(rstp_2023.bridge(0,helpers.generate_mac(0),4))
        pass

    @classmethod
    def tearDownClass(cls):
        print('tearDownClass')
#        print("TEST: tearDown")
#        helpers.terminate_bridge(self.bridges,0)
        pass

    #run it's before every single test
   # def setUp(self):
#        print("TEST: setUp")
   #     self.bridges = []
        #will be using second bridge for testing
  #      self.bridges.append(rstp_2023.bridge(0,helpers.generate_mac(0),4))
#        pass

    #run it's code after every single test
#    def tearDown(self):
#        print("TEST: tearDown")
#        helpers.terminate_bridge(self.bridges,0)
#        pass

    # TEST: from root become not root
    # TEST: port role must transit to "Root"
    # TEST: become root

    def test_become_not_root_bridge(self):
        print("test_become_not_root_bridge")
        #br = self.bridges[0]
        br = bridges[0]
        pass
        # br.ports[0].rcvdInfoWhile=6
        # br.ports[0].message_age = "0000"
        # br.ports[0].rcvdFlags = "3c"
        # br.ports[0].root_priority = "4096"
        # br.ports[0].root_mac = "505060708090"
        # br.ports[0].designated_bridge_priority = "8192"
        # br.ports[0].designated_bridge_mac = "f92323232323"
        # br.ports[0].designated_bridge_port_id = "8001"
        # int_path_cost = 20000+int(br.ports[0].port_cost,16)
        # str_path_cost = f'{int_path_cost:08x}'
        # br.ports[0].root_path_cost = str_path_cost
        # br.ports[0].received_root_path_cost = "00004e20"
        # br.ports[0].port_hello_time = "02"
        # br.ports[0].port_max_age = "1400"
        # br.ports[0].port_forward_delay = "0f00"

        self.bpdu = bytearray.fromhex("0180c20000005254aa1caabb00294242030000020\
                23c10015254aa1caabb0000000010015254aa1caabb80030000140002000f00000000")
        self.sckt = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        self.sckt.bind(("rstp_0_0", ETH_P_ALL))
        sendbytes = self.sckt.send(self.bpdu)
        time.sleep(1)
        self.assertEqual(br.i_am_root, False)               # Test become not root.
        self.assertEqual(br.ports[0].port_role, "Root")     # Test port transition to root.
        time.sleep(16)                                     # Bridge must by default time out after 6 seconds to root.
        self.assertEqual(br.i_am_root, True)                # Test rrWhile (15 seconds). When nothing received, bridge becomes root
        self.sckt.close()

#    def test_set_max_age(self):
#        print("test_set_max_age")
#        br = self.bridges[0]
#        br.set_max_age(0)
#        self.assertEqual(br.max_age,"1400")         
#        br.set_max_age(1)
#        self.assertEqual(br.max_age, "0100")
#        br.set_max_age(20)
#        self.assertEqual(br.max_age,"1400")         
#        br.set_max_age(-1)
#        self.assertEqual(br.max_age,"1400")
#        br.set_max_age(21)
#        self.assertEqual(br.max_age,"1400")                 # should not set as 20 is max

#    def test_set_hello_time(self):                          #must start with test_
#        print("test_set_hello_time")
#        br = self.bridges[0]

#        br.set_hello_time(0)
#        self.assertEqual(br.hello_time,"0200")
#        br.set_hello_time(1)
#        self.assertEqual(br.hello_time,"0100")
#        br.set_hello_time(20)
#        self.assertEqual(br.hello_time,"1400")
#        br.set_hello_time(-1)
#        self.assertEqual(br.hello_time,"1400")
#        br.set_hello_time(21)
#        self.assertEqual(br.hello_time,"1400")


#    def test_set_forward_delay(self):
#        print("test_set_forward_delay")
#        br = self.bridges[0]
#        br.set_forward_delay(0)
#        self.assertEqual(br.forward_delay,"0f00")
#        br.set_forward_delay(1)
#        self.assertEqual(br.forward_delay,"0100")
#        br.set_forward_delay(20)
#        self.assertEqual(br.forward_delay,"1400")
#        br.set_forward_delay(-1)
#        self.assertEqual(br.forward_delay,"1400")
#        br.set_forward_delay(21)
#        self.assertEqual(br.forward_delay,"1400")

#    def test_set_port_priority(self):
#        print("test_set_port_priority")
#        br= self.bridges[0]
#        br.ports[0].set_port_priority(0)
#        self.assertEqual(br.ports[0].port_priority, "80")
#        br.ports[0].set_port_priority(1)
#        self.assertEqual(br.ports[0].port_priority, "01")
#        br.ports[0].set_port_priority(255)
#        self.assertEqual(br.ports[0].port_priority, "ff")  
#        br.ports[0].set_port_priority(-1)
#        self.assertEqual(br.ports[0].port_priority, "ff")
#        br.ports[0].set_port_priority(256)
#        self.assertEqual(br.ports[0].port_priority, "ff")

#    def test_set_bridge_priority(self):
#        print("test_set_bridge_priority")
#        br = self.bridges[0]
#        br.set_bridge_priority(0)
#        self.assertEqual(br.bridge_priority,"8001")              # priority is 8000, 1 is VLAN (out of scope, always 1)
#        br.set_bridge_priority(543)
#        self.assertEqual(br.bridge_priority,"8001")              # priority is 8000, 1 is VLAN
#        br.set_bridge_priority(4096)
#        self.assertEqual(br.bridge_priority,"1001")              # priority is 8000, 1 is VLAN
#        br.set_bridge_priority(61440)
#        self.assertEqual(br.bridge_priority,"f001")              # priority is 8000, 1 is VLAN
#        br.set_bridge_priority(-4096)
#        self.assertEqual(br.bridge_priority,"f001")              # priority is 8000, 1 is VLAN
#        br.set_bridge_priority(65536)
#        self.assertEqual(br.bridge_priority,"f001")              # priority is 8000, 1 is VLAN
        

#    def test_set_cost_on_port(self):
#        print("test_set_cost_on_port")
#        br = self.bridges[0]
#        br.ports[0].set_port_cost(-1)
#        self.assertEqual(br.ports[0].port_cost, "00004e20")
#        br.ports[0].set_port_cost(0)
#        self.assertEqual(br.ports[0].port_cost, "00004e20")
#        br.ports[0].set_port_cost(40000)
#        self.assertEqual(br.ports[0].port_cost, "00061a80")
#        br.ports[0].set_port_cost(200000000)
#        self.assertEqual(br.ports[0].port_cost, "0bebc200")
#        br.ports[0].set_port_cost(200000001)
#        self.assertEqual(br.ports[0].port_cost, "00004e20")

    def test_bpdu_on_port(self):
        print("test bpdu format")
        br = self.bridges[0]


        print(br.ports[0].get_bpdu_str())
        br.set_bridge_priority(4096)
        br.set_max_age(15)
        br.set_hello_time(6)
        br.set_forward_delay(10)
        #br.ports[0].set_port_priority(10)
        print(br.ports[0].get_bpdu_str())
        print("port pr set to"+br.ports[0].port_priority)
        bpdu_must_be = bytearray(bytes([0x01,0x80,0xc2,0x00,0x00,0x00,0xaa,0xbb,0xcc,0xdd,0xee,0x00,\
                0x00,0x29,0x42,0x42,0x03,0x00,0x00,0x02,0x02,0x0e,0x10,0x01,0xaa,\
                0xbb,0xcc,0xdd,0xee,0x00,0x00,0x00,0x00,0x00,0x10,0x01,0xaa,0xbb,\
                0xcc,0xdd,0xee,0x00,0x0a,0x00,0x00,0x00,0x0f,0x00,0x06,0x00,0x0a,\
                0x00,0x00,0x00,0x00]))
        print(br.ports[0].get_bpdu_str())
        self.assertEqual(br.ports[0].get_bpdu(),bpdu_must_be)
if __name__ == '__main__':
    unittest.main()
