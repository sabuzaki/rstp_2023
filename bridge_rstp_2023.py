#DEFAULT_BRIDGE_PRIORITY = "8001"
#PORTS_PER_BRIDGE = 8
from port_rstp_2023 import port
from transmit_rstp_2023 import port_transmit_state_machine
from receive_rstp_2023 import port_receive_state_machine
from helpers_rstp_2023 import logger
import helpers_rstp_2023 as helpers
from timer_rstp_2023 import port_timer_state_machine
from role_rstp_2023 import port_role_transition_state_machine
import socket
import os

DEFAULT_BRIDGE_PRIORITY = "8001"
#PORTS_PER_BRIDGE = 8
DEFAULT_PORT_ID = "0500"
BUFFER_SIZE = 65536
MAX_AGE_STATIC = 20                # integer
MAX_FORWARD_DELAY_STATIC = 20       # integer
MAX_HELLO_TIME_STATIC = 20          # integer
MAX_FORWARD_DELAY_STATIC = 20       # integer
buffer = BUFFER_SIZE * 0
PRIORITY_LIST = [0,4096,8192,12288,16384,20480,24576,28672,32768,36864,40960,45056,49152,53248,57344,61440] # available values as priority

#class priority_vector():
#    priority = "8001"
#    def __init__(self,mac):
#        self.root_mac=mac

#class bridge_priority_vector():
#    def __init__(self,

#class port_priority_vector(priority_vector):
#    def

class root_priority_vector():

    def __init__(self,bridge_mac):
        self.root_priority = "8001"
        self.root_mac = bridge_mac
        self.root_cost = "00000000"
        self.designated_bridge_priority = "ffff"
        self.designated_bridge_mac = "ffffffffffff"
        self.designated_bridge_port_id = "ffff"
        self.root_port_id = "ffff"

    def reset_root_priority_vector(self,priority,mac):
        self.root_priority = priority
        self.root_mac = mac
        self.root_cost = "00000000"
        self.designated_bridge_priority = "ffff"
        self.designated_bridge_mac = "ffffffffffff"
        self.designated_bridge_port_id = "ffff"
        self.root_port_id = "ffff"

class bridge():
    def __init__(self,bridge_nr,mac,port_count):
        self.i_am_root = True
        self.bridge_nr = bridge_nr              # 0,1,2,3,4,5,6,etc....
#        self.bridge_mac = helpers.generate_mac()
        self.bridge_mac = mac
        self.bridge_priority = DEFAULT_BRIDGE_PRIORITY
        self.bridge_id = self.bridge_priority + self.bridge_mac
        self.shutdown = False

        # below settings updated and used in the message when received superior BPDU

        self.max_age = "1400"                           # default 20 seconds
        self.forward_delay = "0f00"                     # default 15 seconds
        self.hello_time = "0200"                         # Hello Timer - how often to send BPDUs on each port. default: 2 seconds
        self.tcCounter = 0
        self.tcSince = 0
        self.tc = False

        #self.tcWhile = int(self.forward_delay[0:2],16)
        self.tcWhile = int(self.hello_time[0:2],16)*3

        self.version_1 = "00"
        self.version_2 = "0000"
        self.ports = []

        # root path priority vector
        #self.root_port = False

        print("Bridge-"+str(bridge_nr)+" initialization: Bridge ID "+ self.bridge_priority+"."+self.bridge_mac+"..."+"Initializing "+\
            str(port_count)+" ports")

        self.transmit_threads = []
        self.receive_threads = []
        self.root_pr_vector = root_priority_vector(self.bridge_mac)
        for i in range(0,port_count):
            self.ports.append(port(self,i))                       # port[0].port_nr == 0
            self.ports[i].start()                                   # port information state machine x4 per bridge (total x16)
            sckt = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
            self.transmit_threads.append(port_transmit_state_machine(self.ports[i],sckt))
            self.transmit_threads[i].start()
            self.receive_threads.append(port_receive_state_machine(self.ports[i],sckt))
            self.receive_threads[i].start()

        print("Starting bridge logger...")
        self.this_logger = logger()

        print("Starting port timer state machines...")
        self.timer_thread = port_timer_state_machine(self)
        self.timer_thread.start()
        print("Starting port role transition state machines...")
        self.role_selection_thread = port_role_transition_state_machine(self)
        self.role_selection_thread.start()
        #topology_change_state_machine(self).start()

    #def get_l2(self):
    #    return bytearray.fromhex(self.l2)
    def set_sync_tree(self):
        for p in self.ports:
            if(p.port_id != self.root_pr_vector.port_id):
                p.sync = True
                p.synced = False

    def update_root_pr_vector(self,r_pr_id):
        root_port_nr = int(r_pr_id[2:4],16)
        self.root_pr_vector.root_priority = self.ports[root_port_nr].root_priority
        self.root_pr_vector.root_mac = self.ports[root_port_nr].root_mac
        int_path_cost = int(self.ports[root_port_nr].received_root_path_cost,16)+int(self.ports[root_port_nr].port_cost,16)
        str_path_cost = f'{int_path_cost:08x}'
        self.root_pr_vector.root_cost = str_path_cost
#        self.root_pr_vector.root_path_cost = self.ports[root_port_nr].root_path_cost
        self.root_pr_vector.designated_bridge_priority = self.ports[root_port_nr].designated_bridge_priority
        self.root_pr_vector.designated_bridge_mac = self.ports[root_port_nr].designated_bridge_mac
        self.root_pr_vector.designated_bridge_port_id = self.ports[root_port_nr].designated_bridge_port_id
        self.root_pr_vector.root_port_id = r_pr_id
    def get_root_pr_vector(self):
        return self.root_pr_vector.root_priority+self.root_pr_vector.root_mac+self.root_pr_vector.root_cost+self.root_pr_vector.designated_bridge_priority\
            +self.root_pr_vector.designated_bridge_mac+self.root_pr_vector.designated_bridge_port_id+self.root_pr_vector.root_port_id

    def set_bridge_priority(self,var):
        if(var in PRIORITY_LIST):
            var = var+1                                     # priority is plus system ID. It is observed all cisco switches set system ID to 1. Thus priority always incremented by one
            self.bridge_priority = str(f'{var:04x}')
            self.bridge_id = self.bridge_priority+self.bridge_mac
        else:
            print("Incorrect. Value "+str(var)+" is not in "+str(PRIORITY_LIST))
        if(self.i_am_root):
            self.root_pr_vector.root_priority = self.bridge_priority
            for p in self.ports:
                p.root_priority = self.bridge_priority

    def get_best_port_priority_vector(self):
        # return will never be this string. if all ports having the same priority vector (Ie I'am root and not connected to any other bridge)
        # then best port priority vector will always be the last of the port.
        best = "ffffffffffffffffffffffffffffffffffffffffffffffff"           
        elected_best_port_nr = 0
        #v = []
        for p in self.ports:
            while(p.rcvdMsg==True):         # if received just now message, and info is updated by the port class (withing message_check())
                pass
            vector = p.get_port_priority_vector()

            if(p.portEnabled and vector<best):
                if(p.rootguard and vector[24:44]!="ffffffffffffffffffff"):              # If rootguard enabled on port, and it's vector is NOT in default state (did not receive any BPDUs)
                    p.reset_port_priority_vector()
                    p.port_role = "Disabled"
                    p.port_state = "Err_disabled"
                    p.this_logger.log_string("JJJJJJJJJJJJJJJ: Err_disabled set ON p.port_state")
                else:
                    best=vector
                    elected_best_port_nr = p.port_nr

                # below if has purpose of tackling "ghost bpud loop within topology when root bridge priority is increased". It is not clear how helpful it is
                # but it makes sure that when looping through ports and looking for best vector, when two identical root_mac addresses found, vector returned
                # which has lower cost path to root rather than one which has lower priority.
    #            if(vector[4:15]==best[4:15]):               # if there are two ports having same root mac (alternate and root)
    #                if(vector[15:23]<best[15:23]):          # if root_path_cost of vector is lower than of best
    #                    best=vector
    #                    elected_best_port_nr = p.port_nr
    #            elif(vector<best):
    #                best=vector
    #                elected_best_port_nr = p.port_nr
        #mn = min(v)
        #elected_best_port_nr = mn.port_nr
        return elected_best_port_nr, best

    def transition_to_not_root_bridge(self,elected_best_port_nr):
        self.tcSince = 0                    # topology change since timer. Does not affect anything. Incresed every 1 second.
        self.tcCounter = self.tcCounter+1   # does not affect anything. Counts how many topology changes happened during bridge lifespan.
        self.tc = True                  # ...
        self.tcWhile = int(self.hello_time[0:2],16)*3
        #self.tcWhile = int(self.forward_delay[0:2],16)
        self.this_logger.log_string("set_root_priority_vector: I became NOT root. root_pr_vector: "+self.get_root_pr_vector())
        self.update_root_pr_vector(self.ports[elected_best_port_nr].port_id)
        self.ports[elected_best_port_nr].rrWhile = int(self.forward_delay[0:2],16)
        self.i_am_root = False
        #self.root_pr_vector.reset_root_priority_vector(self.bridge_priority,self.bridge_mac)
        # reset all NON ROOT ports. They will enter Discarding/Listening/Learning state, or will enter agreement/proposal stage to\
        # transition to Learning immediately if there is another bridge on that port.
        for p in self.ports:
            p.flags = helpers.set_binary_bit(helpers.strhex_to_bin(p.flags), 7, "1") # set TCN flag xxxxxxx1
            if(p.port_nr != elected_best_port_nr):
                p.reset_port_priority_vector()
        self.this_logger.log_string("HHHHHHHHHH transitioning gto not root bridge: root port priority vector: "+self.ports[elected_best_port_nr].get_port_priority_vector())

    def change_root_port(self,elected_best_port_nr):
        self.update_root_pr_vector(self.ports[elected_best_port_nr].port_id)
        self.ports[elected_best_port_nr].rrWhile = int(self.forward_delay[0:2],16)
        if(not self.tc):                        # if topology change was recorded already(above), DO NOT increase counter 
            self.tcCounter = self.tcCounter+1
            self.tc = True                      # if root port changes, Topology change started
            self.tcWhile = int(self.hello_time[0:2],16)*3
#            self.tcWhile = int(self.forward_delay[0:2],16)
            self.tcSince = 0                    # topology change since timer. does not affect anything
        self.reroot = True
        # reset all NON ROOT ports. They will enter Discarding/Listening/Learning state, or will enter agreement/proposal stage to\
        # transition to Learning immediately if there is another bridge on that port.
        for p in self.ports:
            p.flags = helpers.set_binary_bit(helpers.strhex_to_bin(p.flags), 7, "1") # set TCN flag xxxxxxx1
            if(p.port_nr != elected_best_port_nr):
                p.reset_port_priority_vector()

    def assign_root_port(self):
       # deal with root port
       root_port_nr = int(self.root_pr_vector.root_port_id[2:4],16)
       # port class dealing with agreement/proposal issue. start forwarding&learning only when agreed flag is set to true. Otherwise


       flags = self.ports[root_port_nr].flags

       if(self.ports[root_port_nr].agreed):
           self.ports[root_port_nr].port_state="Forwarding"
           self.ports[root_port_nr].this_logger.log_string("BBBBBBBBBBBBBBB: set port state Forwarding")
           flags = helpers.set_binary_bit(helpers.strhex_to_bin(flags), 2, "1") # forwarding: yes
           flags = helpers.set_binary_bit(helpers.strhex_to_bin(flags), 3, "1") # learning: yes


       flags = helpers.set_binary_bit(helpers.strhex_to_bin(flags), 4, "1") # set root port role flag: xxxx1xxx
       flags = helpers.set_binary_bit(helpers.strhex_to_bin(flags), 5, "0") # set root port role flag: xxxxx0xx

       flags = helpers.set_binary_bit(helpers.strhex_to_bin(flags), 6, "0") # set root port role (Proposal) flag: xxxxxx0x. Root port never proposing.
       self.ports[root_port_nr].flags = flags
       self.ports[root_port_nr].port_role="Root"

    # method also sets bridge as root or not_root
    # otherwise it sets root_pr_vector of bridge object to the port values,
    # of a port which received the lowest "root vector" (lowest priority+mac of root bridge)
    def set_root_priority_vector(self):
        #all_ports = []
        elected_best_port_nr, best = self.get_best_port_priority_vector() 

#        self.this_logger.log_string("set_root_priority_vector: best port priority vector is: "+best)
#        self.this_logger.log_string("set_root_priority_vector: my bridge priority vector is: "+self.bridge_priority+self.bridge_mac)

        # comparing best root path priority vector VS bridge priority vector (bridgeID)
        temp_best_port = self.ports[elected_best_port_nr]
        # If best root vector is better than this bridge vector
        # Topology considered changed IF: 1) root port changed 2) this bridge changed status from root to not_root or vise versa 
        # to....

#        current_root_port_nr = int(self.root_pr_vector.root_port_id[2:4],16)            # commented 19thfeb
#        if(current_root_port_nr != 255):             # commented 19th feb
#            current_root_priority_vector = self.ports[current_root_port_nr].get_port_priority_vector() # commented 19th feb
#        else: current_root_priority_vector = "ffffffffff"      # commented 19th feb

        if((temp_best_port.root_priority+temp_best_port.root_mac) < (self.bridge_priority + self.bridge_mac)):
            #if(self.i_am_root != False):
            # transition to not_root_bridge if i_am_root variable is not False yet or
            # if the root port changed
#            if(self.i_am_root != False or (best != current_root_priority_vector)): #commented 19thfeb
            if(self.i_am_root != False):                # returned on 19th feb
                self.transition_to_not_root_bridge(elected_best_port_nr)
            else: pass          # I am  not already
#                self.this_logger.log_string("set_root_priority_vector: I was NOT root already...do nothing.")
                #self.tc = False

            #If best port vector is not the same as root_pr_vector port number (root port changed)
            if(self.i_am_root == False and elected_best_port_nr != int(self.root_pr_vector.root_port_id[2:4],16)):              # If other bridge was root and my root port changed (best port priority vector is different now)
                self.change_root_port(elected_best_port_nr)
#                print("Bridge class HHHHHHHHHHHHHHHHHHHHHHHHHHHHHH changing root port")
            #else: self.tc = False

        # else: This bridge vector is better than any found on ports
        else:
            # if: If I was not root and must become root
            if(self.i_am_root!=True):
                self.become_a_root()
            else: pass
                #self.tc = False
#                self.this_logger.log_string("set_root_priority_vector: I was root already... do nothing.")
                
    def become_a_root(self):
        self.tcCounter = self.tcCounter+1
        self.tcSince = 0                # topology change since timer. does not affect anything
        self.tcWhile = int(self.hello_time[0:2],16)*3
#        self.tcWhile = int(self.forward_delay[0:2],16)
        self.i_am_root = True
        self.this_logger.log_string("set_root_priority_vector: I became root.")
        self.tc = True
#                self.root_port = False
        for p in self.ports:
#                    print("ZZZZZZZ RESETTTTTTTTING PORT: "+p.port_name)
            p.reset_port_priority_vector()
#            p.flags = helpers.set_binary_bit(helpers.strhex_to_bin(p.flags), 7, "1") # set TCN flag xxxxxxx1
        self.root_pr_vector.root_priority = self.bridge_priority
        self.root_pr_vector.root_mac = self.bridge_mac
        self.root_pr_vector.root_cost  = "00000000"
        self.root_pr_vector.designated_bridge_priority = "ffff"
        self.root_pr_vector.designated_bridge_mac = "ffffffffffff"
        self.root_pr_vector.designated_bridge_port_id = "ffff"
        self.this_logger.log_string("I became root: current best port root vector:"+self.get_root_pr_vector()+"; my vector:"+self.bridge_priority+self.bridge_mac)

    def connect_to_network_card(self,port_nr,network_card_name):
#        self.ports[port_nr].port_name = network_card_name
        self.ports[port_nr].peer_name = network_card_name
        print("ip link set "+self.ports[port_nr].peer_name+" up")
        os.system("ip link set "+self.ports[port_nr].peer_name+" up")
        print("ip link set "+self.ports[port_nr].peer_name+" allmulticast on")
        os.system("ip link set "+self.ports[port_nr].peer_name+" allmulticast on")

    def connect_port_to_port(self,pr_int,peer_port_object):
        p = peer_port_object

        if(p.peer_name!="None"):               # disconnect a peers port from another connection
            a=p.peer_port;
            #print("peer : "+p.peer_name)
            #print("peer of a peer: "+a.peer_name)
            a.reset_port_connectivity()
            p.reset_port_connectivity()                       # reset peer port

        if(self.ports[pr_int].peer_name!="None"):
            self.ports[pr_int].peer_port.reset_port_connectivity()              # reset already connected peer
            self.ports[pr_int].reset_port_connectivity()

        if(self.ports[pr_int].peer_name=="None" and peer_port_object.peer_name=="None"):
            self.ports[pr_int].peer_name=peer_port_object.port_name
            peer_port_object.peer_name = self.ports[pr_int].port_name
            self.ports[pr_int].peer_port = peer_port_object               # initially every port had peer name, but more efficient to keep object of peer port.
            peer_port_object.peer_port = self.ports[pr_int]


        #print("Shutting down dummy network cards: "+self.ports[pr_int-1].port_name+" and "+peer_port_object.port_name)
        os.system("ip link set "+self.ports[pr_int].port_name+" down")
        os.system("ip link set "+peer_port_object.port_name+" down")
        #print("ip link del "+self.ports[pr_int-1].port_name)
        os.system("ip link del "+self.ports[pr_int].port_name)
        #print("ip link del "+peer_port_object.port_name)
        os.system("ip link del "+peer_port_object.port_name)
        #print("Creating veth (virtual network) card with a peer...")
        os.system("ip link add "+self.ports[pr_int].port_name+" type veth peer name "+peer_port_object.port_name)
        #print("Starting network cards: "+self.ports[pr_int-1].port_name+", "+peer_port_object.port_name)
        os.system("ip link set "+peer_port_object.port_name+" up")
        os.system("ip link set "+self.ports[pr_int].port_name+" up")

        self.ports[pr_int].peer_port = peer_port_object
        self.ports[pr_int].peer_name = peer_port_object.port_name

        peer_port_object.peer_port = self.ports[pr_int]
        peer_port_object.peer_name = self.ports[pr_int].port_name

    def set_max_age(self,var):
        if(var >=1 and var <= MAX_AGE_STATIC):
            self.max_age = str(f'{var:02x}')+"00"
#            self.send_change_signal()
        else:
            print("Incorrect value")

    def set_hello_time(self,var):
        if(var >=1 and var <= MAX_HELLO_TIME_STATIC):
            self.hello_time = str(f'{var:02x}')+"00"
#            self.send_change_signal()
        else:
            print("Incorrect value")

    def set_forward_delay(self,var):
        if(var >=1 and var <= MAX_FORWARD_DELAY_STATIC):
            self.forward_delay = str(f'{var:02x}')+"00"
#            self.send_change_signal()
        else:
            print("Incorrect value")
