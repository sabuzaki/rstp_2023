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
        #will be using second bridge for testing
        self.bridges.append(rstp_2023.bridge(0,helpers.generate_mac(0),4))
        pass

    #run it's code after every single test
    def tearDown(self):
        print("TEST: tearDown")
        helpers.terminate_bridge(self.bridges,0)
        pass

    #PRIORITY_LIST = [0,4096,8192,12288,16384,20480,24576,28672,32768,36864,40960,45056,49152,53248,57344,61440]
    def test_set_set_bridge_priority(self):
        cl = cli_menu()
        br = self.bridges[0]

        sys.stdin = StringIO("0\n0\n")
        cl.print_menu(self.bridges,10)
        self.assertEqual(br.bridge_priority, "0001")

        sys.stdin = StringIO("0\n543\n")
        cl.print_menu(self.bridges,10)
        self.assertEqual(br.bridge_priority, "0001")

        sys.stdin = StringIO("0\n4096\n")
        cl.print_menu(self.bridges,10)
        self.assertEqual(br.bridge_priority, "1001")

        sys.stdin = StringIO("0\n61440\n")
        cl.print_menu(self.bridges,10)
        self.assertEqual(br.bridge_priority, "f001")

        sys.stdin = StringIO("0\n-4096\n")
        cl.print_menu(self.bridges,10)
        self.assertEqual(br.bridge_priority, "f001")

        sys.stdin = StringIO("0\n65536\n")
        cl.print_menu(self.bridges,10)
        self.assertEqual(br.bridge_priority, "f001")

    def test_set_max_age(self):         # Test 1-...
        print("test_set_max_age")
        cl = cli_menu()
        br = self.bridges[0]

        sys.stdin = StringIO("0\n0\n")
        cl.print_menu(self.bridges,11)
        self.assertEqual(br.max_age, "1400")

        sys.stdin = StringIO("0\n1\n")
        cl.print_menu(self.bridges,11)
        self.assertEqual(br.max_age, "0100")

        sys.stdin = StringIO("0\n20\n")
        cl.print_menu(self.bridges,11)
        self.assertEqual(br.max_age, "1400")

        sys.stdin = StringIO("0\n-1\n")
        cl.print_menu(self.bridges,11)
        self.assertEqual(br.max_age, "1400")

        sys.stdin = StringIO("0\n21\n")
        cl.print_menu(self.bridges,11)
        self.assertEqual(br.max_age, "1400")

    def test_set_hello_time(self):                          #must start with test_
        print("test_set_hello_time")
        cl = cli_menu()
        br = self.bridges[0]

        sys.stdin = StringIO("0\n0\n")
        cl.print_menu(self.bridges,12)
        self.assertEqual(br.hello_time, "0200")

        sys.stdin = StringIO("0\n1\n")
        cl.print_menu(self.bridges,12)
        self.assertEqual(br.hello_time, "0100")

        sys.stdin = StringIO("0\n20\n")
        cl.print_menu(self.bridges,12)
        self.assertEqual(br.hello_time, "1400")

        sys.stdin = StringIO("0\n-1\n")
        cl.print_menu(self.bridges,12)
        self.assertEqual(br.hello_time, "1400")

        sys.stdin = StringIO("0\n21\n")
        cl.print_menu(self.bridges,12)
        self.assertEqual(br.hello_time, "1400")

    def test_set_forward_delay(self):
        print("test_set_forward_delay")
        cl = cli_menu()
        br = self.bridges[0]

        sys.stdin = StringIO("0\n0\n")
        cl.print_menu(self.bridges,13)
        self.assertEqual(br.forward_delay, "0f00")

        sys.stdin = StringIO("0\n1\n")
        cl.print_menu(self.bridges,13)
        self.assertEqual(br.forward_delay, "0100")

        sys.stdin = StringIO("0\n20\n")
        cl.print_menu(self.bridges,13)
        self.assertEqual(br.forward_delay, "1400")

        sys.stdin = StringIO("0\n-1\n")
        cl.print_menu(self.bridges,13)
        self.assertEqual(br.forward_delay, "1400")

        sys.stdin = StringIO("0\n21\n")
        cl.print_menu(self.bridges,13)
        self.assertEqual(br.forward_delay, "1400")

    def test_set_cost_on_port(self):
        print("test_set_cost_on_port")
        cl = cli_menu()
        br = self.bridges[0]

        sys.stdin = StringIO("0\n0\n0\n")
        cl.print_menu(self.bridges,14)
        self.assertEqual(br.ports[0].port_cost, "00004e20")

        sys.stdin = StringIO("0\n0\n1\n")
        cl.print_menu(self.bridges,14)
        self.assertEqual(br.ports[0].port_cost, "00000001")

        sys.stdin = StringIO("0\n0\n200000000\n")
        cl.print_menu(self.bridges,14)
        self.assertEqual(br.ports[0].port_cost, "0bebc200")

        sys.stdin = StringIO("0\n0\n-1\n")
        cl.print_menu(self.bridges,14)
        self.assertEqual(br.ports[0].port_cost, "0bebc200")

        sys.stdin = StringIO("0\n0\n200000001\n")
        cl.print_menu(self.bridges,14)
        self.assertEqual(br.ports[0].port_cost, "0bebc200")

    def test_set_port_priority(self):
        print("test_set_port_priority")
        cl = cli_menu()
        br= self.bridges[0]

        sys.stdin = StringIO("0\n0\n0\n")
        cl.print_menu(self.bridges,15)
        self.assertEqual(br.ports[0].port_priority, "80")
        self.assertEqual(br.ports[0].port_id, "8000")

        sys.stdin = StringIO("0\n0\n1\n")
        cl.print_menu(self.bridges,15)
        self.assertEqual(br.ports[0].port_priority, "01")
        self.assertEqual(br.ports[0].port_id, "0100")

        sys.stdin = StringIO("0\n0\n255\n")
        cl.print_menu(self.bridges,15)
        self.assertEqual(br.ports[0].port_priority, "ff")
        self.assertEqual(br.ports[0].port_id, "ff00")

        sys.stdin = StringIO("0\n0\n-1\n")
        cl.print_menu(self.bridges,15)
        self.assertEqual(br.ports[0].port_priority, "ff")
        self.assertEqual(br.ports[0].port_id, "ff00")

        sys.stdin = StringIO("0\n0\n256\n")
        cl.print_menu(self.bridges,15)
        self.assertEqual(br.ports[0].port_priority, "ff")
        self.assertEqual(br.ports[0].port_id, "ff00")

    def test_set_root_guard(self):
        cl = cli_menu()
        br = self.bridges[0]

        sys.stdin = StringIO("0\n0\n1\n")
        cl.print_menu(self.bridges,16)
        self.assertEqual(br.ports[0].rootguard, True)

    def test_set_bpdu_guard(self):
        cl = cli_menu()
        br = self.bridges[0]

        sys.stdin = StringIO("0\n0\n1\n")
        cl.print_menu(self.bridges,17)
        self.assertEqual(br.ports[0].bpduguard, True)

    def test_set_speed(self):
        cl = cli_menu()
        br = self.bridges[0]

        sys.stdin = StringIO("0\n0\n1\n")
        cl.print_menu(self.bridges,18)
        self.assertEqual(br.ports[0]._speed, 10000000000)
        self.assertEqual(br.ports[0].port_cost, "00000002")

        sys.stdin = StringIO("0\n0\n2\n")
        cl.print_menu(self.bridges,18)
        self.assertEqual(br.ports[0]._speed, 1000000000)
        self.assertEqual(br.ports[0].port_cost, "00000014")

        sys.stdin = StringIO("0\n0\n3\n")
        cl.print_menu(self.bridges,18)
        self.assertEqual(br.ports[0]._speed, 100000000)
        self.assertEqual(br.ports[0].port_cost, "000000c8")

       
        sys.stdin = StringIO("0\n0\n4\n")
        cl.print_menu(self.bridges,18)
        self.assertEqual(br.ports[0]._speed, 10000000)
        self.assertEqual(br.ports[0].port_cost, "000007d0")

        sys.stdin = StringIO("0\n0\n5\n")
        cl.print_menu(self.bridges,18)
        self.assertEqual(br.ports[0]._speed, 1000000)
        self.assertEqual(br.ports[0].port_cost, "00004e20")

        sys.stdin = StringIO("0\n0\n6\n")
        cl.print_menu(self.bridges,18)
        self.assertEqual(br.ports[0]._speed, 100000)
        self.assertEqual(br.ports[0].port_cost, "00030d40")

        sys.stdin = StringIO("0\n0\n7\n")
        cl.print_menu(self.bridges,18)
        self.assertEqual(br.ports[0]._speed, 10000)
        self.assertEqual(br.ports[0].port_cost, "001e8480")

    def test_set_link_duplex(self):
        cl = cli_menu()
        br = self.bridges[0]

        sys.stdin = StringIO("0\n0\n2\n")
        cl.print_menu(self.bridges,19)
        self.assertEqual(br.ports[0].duplex, "Half")
        self.assertEqual(br.ports[0].port_type, "Shared")

        sys.stdin = StringIO("0\n0\n1\n")
        cl.print_menu(self.bridges,19)
        self.assertEqual(br.ports[0].duplex, "Full")
        self.assertEqual(br.ports[0].port_type, "P2P")


    def test_set_portfast(self):
        cl = cli_menu()
        br = self.bridges[0]

        sys.stdin = StringIO("0\n0\n1\n")
        cl.print_menu(self.bridges,20)
        self.assertEqual(br.ports[0].portfast, True)

        sys.stdin = StringIO("0\n0\n2\n")
        cl.print_menu(self.bridges,20)
        self.assertEqual(br.ports[0].portfast, False)

    def test_enable_disable_port(self):
        cl = cli_menu()
        br = self.bridges[0]

        sys.stdin = StringIO("0\n0\n2\n")
        cl.print_menu(self.bridges,21)
        self.assertEqual(br.ports[0].portEnabled, False)
        self.assertEqual(br.ports[0].port_state, "Disabled")
        self.assertEqual(br.ports[0].port_role, "Disabled")

        sys.stdin = StringIO("0\n0\n1\n")
        cl.print_menu(self.bridges,21)
        self.assertEqual(br.ports[0].portEnabled, True)
        self.assertEqual(br.ports[0].port_state, "Discarding")
        self.assertEqual(br.ports[0].port_role, "Designated")

if __name__ == '__main__':
    unittest.main()
