import threading
from helpers_rstp_2023 import logger
import helpers_rstp_2023 as helpers
import os
import time
RSTP_MULTICAST_DEST = "0180c2000000"
BPDU_LENGTH="0029"
DSASSP = "424203"               # always same.
PROTOCOL_ID = "0000"            # Start of STP/RSTP. Always same.
VERSION = "02"
#import socket
class port(threading.Thread):
    def __init__(self,this_bridge,port_nr):
        self.this_bridge = this_bridge
        self.tick = False               # reset to True every second. This object resets it to False again after doing checks
        self.agreed = False             # dispute is settled. No messages with agreed flag on required
#        self.agreementReceived = False
        self.proposing = True           # I am sending packets with proposal flag on
        self.proposed = False           # Other bridge sending packets with proposal flag on (my port receiving)
#        self.rcvdInfoWhile = int(this_bridge.hello_time[0:2],16)*3 # If this bridge is not a ROOT bridge, this value checked by all ports when last time BPDU
        self.rcvdInfoWhile = 0          # If this bridge is not a ROOT bridge, this value checked by all ports when last time BPDU
                                        # for that port was received. if it reaches 0, port information expires.
        self.rbWhile = 0                #int(self.this_bridge.hello_time[0:2],16)               # x2 hello_timer
        self.rrWhile = 0                #int(self.this_bridge.forward_delay[0:2],16)            # x2 forward_delay
        self.fdWhile = int(self.this_bridge.forward_delay[0:2],16)  # timer for alternate port and to delay port transition....
                                        #set to forward_delay of root bridge ir this bridge. reduced by one every second
        self.txHoldCount = 5                            # Maximum BPDUs per second. When TC is happening, BPDUs are sent at maximum rate for topology change to occure
                                                        # not found in IEEE 802.1w what is recommended value. incremented by each transmission. Set to zero by timer machine
        self.synced = False             # 
#        self.rcvdRSTP = False           # not used.
        self.rcvdMsg = False            # port_receive_state_machine sets it to True when message received and stores it in rcvdContent
        self.rcvdContent = ""
        self.reroot = True
#        self.tc = False                 # not used. Set to True by port state machine when topology change happening. set to False by Topology state machine.
        self.sync = False
        self.synced = True
        self.bridge_nr = this_bridge.bridge_nr
        self.port_nr = port_nr          # number 0 - 3
        self.bpdu_type = "02"           # RSTP
        self.flags = "0e"               # Designated proposing 00001110
        #self.flags = "3e"               # Forwarding/learning/Designated = 3c(. when set to 7c,
                                        # 0... .... Topology change Ack: No #802.1D 17.21.20: The topology flag is never used
                                        # .0.. .... Agreement: No
                                        # ..1. .... Forwarding: Yes
                                        # ...1 .... Learning: Yes
                                        # .... 11.. Port_Role:Designated, 00-Unknown, 01-Alternate/Backup, 10-Root
                                        # .... ..0. Proposal: no
                                        # .... ...0 Topology Change: No
                                        # 7c Agr/For/Lear/Des
                                        # 3c Frw/Lrn/Desg
                                        # 7e Agr/For/Lear/Des/Prop
                                        # 34 Frw/Lrn/Bck-Alt
        #self.agreement = "0"
        self.peer_name = "None"
        self.peer_port = port
        self.message_age = "0000"           # Root bridge sends this value as 0, all subsequent bridges add 1 to the value. For some reason packet trackers calculate it in seconds, but many sources
                                            # indicate that this represents "how many switches/hops this packet is away from the root bridge. If incrementing by 7, message_age looks like: 0700. Or
                                            # if incremented by 10, message_age looks like 0a00 value in hex
        self.rootguard = False              # when received superior BPDU on this port, put it into err_disable state
        self.bpduguard = False              # puts the port into err_disabled state if BPDU arrives onto the port (superior or non-superior)

        self.port_priority = "80"
        self.root_priority = self.this_bridge.bridge_priority
        self.root_mac = self.this_bridge.bridge_mac                                          # root mac is the same as bridge mac during initialization
        self.root_path_cost = "00000000"
        self.received_root_path_cost = "00000000"
        self.designated_bridge_priority = "ffff"
        self.designated_bridge_mac = "ffffffffffff"
        self.designated_bridge_port_id = "ffff"
        self.port_id = self.port_priority+str(f'{self.port_nr:02x}')
#        self.port_message_age = "0000"
        self.port_hello_time = "0000"
        self.port_max_age = "0000"
        self.port_forward_delay = "0000"

        self.duplex = "Full"
#        self.speed = 1000000                         # default 1Gb/s. Port cost 20.000
        self._speed = 1000000
#        self.update_speed(1000000)                         # default 1Gb/s. Port cost 20.000

        self.bridge_settings_changed = False    # this set to True by this_bridge object on all ports[] array
        self.port_name = "rstp_"+str(self.this_bridge.bridge_nr)+"_"+str(self.port_nr)         #secrets.token_hex(2)   # random port name. binds to this virtual dummy network card name
#        self.peer_name = secrets.token_hex(2)               # random peer name.
        self.port_cost = "00004e20"                           # 1 - 200000000
        self.port_cost_set_manually = False                 # If port cost set manually, it is as it is set, if not - it is set depending on the speed value
        self.port_role = "Designated"            # Possible values: Designated, Root, Alternative or Backup
        self.port_state = "Discarding"           # Possible values: Forwarding, Disabled, Discarding
        self.port_type = "P2P"   # Possible values: P2P or Shared
        self.portfast = False               # If set True, does not go through 15x seconds of Discarding then 15x  seconds Learning before moving to Forwarding state. When set to True, transition immediately to Forwarding when port reset or topology changed
#        self.operEdge = False
        self.portEnabled = True
        self.reselect = False

        self.this_logger = logger()

        ############ Create dummy network card in OS
        os.system("ip link del "+self.port_name)            # clean up before creating a dummy port.
        os.system("ip link add "+self.port_name+" type dummy")
        os.system("ip link set "+self.port_name+" up")
        threading.Thread.__init__(self)

    @property
    def speed(self):
        if(self._speed==10000000000):
            return "10 Tb/s"
        elif(self._speed==1000000000):
            return "1 Tb/s"
        elif(self._speed==100000000):
            return "100 Gb/s"
        elif(self._speed==10000000):
            return "10 Gb/s"
        elif(self._speed==1000000):
            return "1 Gb/s"
        elif(self._speed==100000):
            return "100 Mb/s"
        elif(self._speed==10000):
            return "10 Mb/s"
        else: return "0 Mb/s (error"

    @speed.setter
    def speed(self, sp):
        self._speed = sp

#    def update_speed(self,val):
#        self._speed = val

    def run(self):
        while(1):
#            if(self.tick):
            if(self.rcvdMsg == True):                        # port_receive_state_machine sets it to True
                if(self.bpduguard!=True):
                    self.message_check()
                else:
                    if(self.port_state!="Err_disabled"):
                        self.reset_port_priority_vector()
                        self.port_role = "Disabled"
                        self.port_state = "Err_disabled"
#            if(self.rcvdInfoWhile==0 and (self.port_role=="Root")):
            if(self.rrWhile == 0 and (self.port_role=="Root")):
                self.this_logger.log_string("class port.run(): 3333: Resetting port...was Root.")
                self.reset_port_priority_vector()
                self.reroot = True
                #if(i.rcvdInfoWhile==0 and (self.port_role=="Root" or self.port_role=="Alternate")):
            if(self.rbWhile == 0 and self.port_role=="Backup"):
                self.this_logger.log_string("class port.run(): 1344: Resetting port...was Backup.")
                self.reset_port_priority_vector()
            if(self.fdWhile == 0 and (self.port_role=="Alternate")):
                self.this_logger.log_string("class port.run(): 3345: Resetting port...was Alternate.")
                self.reset_port_priority_vector()
            self.rcvdMsg = False

           # self.this_logger.log_string("message_check: my port priority vector is: "+self.get_port_priority_vector)
            time.sleep(0.1)
    ##print(append+"Dest:"+bpdu[0:12]+"|Src:"+bpdu[12:24]+"|Proto_id:"+bpdu[34:38]+"|Ver:"+bpdu[38:40]+"|Type:"+bpdu[40:42]+\
        #"|FLAGS(bin):TCN-"+flags[0]+";AGR-"+flags[1]+";FRW-"+flags[2]+";LRN-"+flags[3]+";RLE-"+flags[4]+flags[5]+";PRP-"+flags[6]+";TCA-"+flags[7]\
        #+"|Root_priority:"\
        #+bpdu[44:48]+"|Root MAC:"+bpdu[48:60]+"|Path cost:\
##        "+bpdu[60:68]+"|Bridge_priority:"+bpdu[68:72]+"|Bridge MAC:"+bpdu[72:84]+"|Root Port:"+bpdu[84:88]\
#        +"|Message Age:"+bpdu[88:92]+"|Max Age:"+bpdu[92:96]+"|Hello Time:"+bpdu[96:100]+"|Forward Delay:\
#        "+bpdu[100:104]+"|Version 1:"+bpdu[104:106]+"|Version 2:"+bpdu[106:110])

    def get_port_priority_vector(self):
        return self.root_priority + self.root_mac + self.root_path_cost + self.designated_bridge_priority + self.designated_bridge_mac\
                    + self.designated_bridge_port_id + self.port_id

    def message_check(self):

        root_bridge_id = self.root_priority+self.root_mac
        designated_bridge_id = self.designated_bridge_priority+self.designated_bridge_mac
        message_root_mac = self.rcvdContent[48:60]
        message_root_priority = self.rcvdContent[44:48]
        message_designated_bridge_port_id = self.rcvdContent[84:88]
        message_root_id = self.rcvdContent[44:60]                         #priority+mac of root bridge received
        message_root_path_cost = self.rcvdContent[60:68]
        message_designated_bridge_mac = self.rcvdContent[72:84]
        message_bridge_id = self.rcvdContent[68:84]                     # designated bridge id
        port_root_id = self.root_priority + self.root_mac
        message_age_int = int(self.rcvdContent[88:90],16)
        rcvdFlags = helpers.strhex_to_bin(self.rcvdContent[42:44])

        #if(self.this_bridge.root_port!=False):
        #    best_root_id = self.this_bridge.root_port.root_priority + self.this_bridge.root_port.root_mac
        #else:
        #    best_root_id = self.this_bridge.bridge_priority + self.this_bridge.bridge_mac
        best_root_id = self.this_bridge.root_pr_vector.root_priority + self.this_bridge.root_pr_vector.root_mac
        # received packet from myself

#        if(message_bridge_id == self.this_bridge.bridge_id):
#            self.rbWhile = int(self.this_bridge.hello_time[0:2],16)*2           # twice as hello time.

        # Below IF is an attempt to solve issue when root priority is incresed, and it's old priority is circulating in the network.
#        if(self.root_mac==message_root_mac and self.root_priority != message_root_priority):                        # if advertised root bridge to this port changed priority
#            self.reset_port_priority_vector()
#            if(self.port_name=="rstp_0_0"):
#                print("NNNNNNNNNNNNNNNNNN reseting port_0_0, root bridge changed priority")
#            return None

        # If message received from the same bridge but not from the same port (meaning two ports connected through the bridge or directly)
        # Set rbWhile (Backup port) timer to forward_delay
        if(message_bridge_id == self.this_bridge.bridge_id and message_designated_bridge_port_id!=self.port_id):
            self.rbWhile = int(self.this_bridge.hello_time[0:2],16)*2
#        if(best_root_id == message_root_id):
#            self.fdWhile = int(self.this_bridge.hello_time[0:2],16)*2
        elif(best_root_id == message_root_id and self.port_role=="Root"):
             self.rrWhile = int(self.this_bridge.forward_delay[0:2],16)
        elif(best_root_id == message_root_id):                              # If this port is not root port, but receiving root bridge advertisement
             self.fdWhile = int(self.this_bridge.forward_delay[0:2],16)
#        if(best_root_id == message_root_id):
             #self.fdWhile = int(self.this_bridge.forward_delay[0:2],16)

        # Below if/else statements are mainly to represent functionality of 802.1D-2004 specification section 17.6
        # It states in which case received message on the port, must be stored as "port priority vector".
        # In one sentence: Port priority vector is updated when received a message with lowest root_priority+root_mac+sender_priority+sender_mac+sender_port_id
        # Port stores this "best message". Then port role seletion thread will detect wihch port has the best port priority vector and compare it with
        # bridge priority vector, thus will decice to stay root bridge or there is another "better" bridge in the LAN with lower/better settings.
        if(not(rcvdFlags[4]=="1" and rcvdFlags[5]=="0")):               # If sending bridge port is having root port role, do NOT update the vector
            if(message_root_mac!=self.this_bridge.bridge_mac):
                if(message_age_int >= 50):                      # message age incremented every hop
                    pass
                elif(message_root_id < root_bridge_id):
                    self.this_logger.log_string("if 3333333333333: update_port_priority_vector")
                    self.update_port_priority_vector()
                    self.check_proposal_agreement_state(rcvdFlags)
                elif((message_root_id==root_bridge_id) and (message_root_path_cost<self.received_root_path_cost)):
                    self.this_logger.log_string("if 222222222222: update_port_priority_vector")
                    self.update_port_priority_vector()
                    self.check_proposal_agreement_state(rcvdFlags)
                elif((message_root_id==root_bridge_id) and (message_root_path_cost==self.received_root_path_cost) and (message_bridge_id<designated_bridge_id)):
                    self.this_logger.log_string("if 77777777777: update_port_priority_vector")
                    self.update_port_priority_vector()
                    self.check_proposal_agreement_state(rcvdFlags)
                elif((message_root_id==root_bridge_id) and (message_root_path_cost==self.received_root_path_cost) and \
    (message_bridge_id==designated_bridge_id) and (message_designated_bridge_port_id[2:4]<self.designated_bridge_port_id[2:4])):
                    self.this_logger.log_string("if 4444444444: update_port_priority_vector")
                    self.update_port_priority_vector()
                    self.check_proposal_agreement_state(rcvdFlags)
                elif((message_designated_bridge_mac==self.designated_bridge_mac) and (message_designated_bridge_port_id[2:4]==self.designated_bridge_port_id[2:4])):      #message came from same bridge
                    self.this_logger.log_string("if 55555: update_port_priority_vector")
                    self.update_port_priority_vector()
                    self.check_proposal_agreement_state(rcvdFlags)
                else:
                    self.this_logger.log_string("707070707070: received something....do nothing...6666")
            else:
                self.this_logger.log_string("8080808080: received advertisement that I'm a root from another bridge")
            

        # Just agree to everything. When received proposal, send agreement.
        # If other bridge not proposing anything, set Agreement and proposal flag to 0

        self.rcvdContent = ""
#        self.rcvdMsg = False

    # As per 802.1d-2004 specification (figure 17-8), the superior bridge only sends proposal down it's the ports at the start of initialization
    # Or when other bridge detected and sending BPDUs on the bridge.
    # Below function's first (if) detects if proposal or agreement was received, then set port object variable to "agreed".
    # "agreed" variable is monitored by port_role_transition_state_machine. If it detects that it's agreed, it transitions immediately to 
    # "Forwarding" state, else (while agreed==False) continue to go through the timers and itermediate port states (Discarding->Learning->Forwarding).
    # when gone through the timers, set agreed=True
    def check_proposal_agreement_state(self,rcvdFlags):

        if(rcvdFlags[6]=="0" or rcvdFlags[1]):      # if proposal is not set in received message or agreement flag is set
        #    print(self.port_id+":"+"agreed")
            self.agreed = True
            self.proposed = False
            self.flags = helpers.set_binary_bit(helpers.strhex_to_bin(self.flags), 1, "0") # set agreement flag x0xxxxxx
            self.flags = helpers.set_binary_bit(helpers.strhex_to_bin(self.flags), 6, "0") # set proposing flag xxxxxx0x
        # If other bridge proposing, set agreement to False, and proposal flag to 0
        if(rcvdFlags[6]=="1" and self.proposed != True): # and self.proposed!=True):                  # Other bridge proposing something....
            self.agreed = False
            self.proposed = True
            self.flags = helpers.set_binary_bit(helpers.strhex_to_bin(self.flags), 1, "1") # set agreement flag x1xxxxxx
            self.flags = helpers.set_binary_bit(helpers.strhex_to_bin(self.flags), 6, "0") # set proposing flag xxxxxx0x

    def update_port_priority_vector(self):
        #if root bridge changed priority
        #if(self.root_mac==self.rcvdContent[48:60] and (self.port_role=="Root" or self.port_role=="Alternate")):              #48:60 - advertised root bridge by another bridge
        #if(self.root_mac==self.rcvdContent[48:60]):

       # If received on Root port, and it's the same root bridge, update priority on all other ports who have their root_mac same. 
        if(self.root_mac==self.rcvdContent[48:60] and (self.port_role=="Root")):
            for p in self.this_bridge.ports:
                if(p.root_mac == self.rcvdContent[48:60]):
                    p.root_priority = self.rcvdContent[44:48]

        # when root bridge sends a message with different root_bridge mac, reset all the ports. must be updated and move to role selection. topology change must be recorded.
        # or if received different root mac on alternate port
        if(self.port_role=="Root" or self.port_role == "Alternate"):
            if(self.rcvdContent[48:60] != self.root_mac):
                #self.this_bridge.root_pr_vector.reset_root_priority_vector(self.this_bridge.bridge_priority,self.this_bridge.bridge_mac)
                for p in self.this_bridge.ports:
                    p.reset_port_priority_vector()
                self.this_bridge.root_pr_vector.reset_root_priority_vector(self.this_bridge.bridge_priority,self.this_bridge.bridge_mac)
                return

                
#        if(self.designated_bridge_mac==self.rcvdContent[72:84]):

#        if(self.port_role=="Alternate"):
#            if(self.rcvdContent[48:60] != self.root_mac):
#                self.reset_port_priority_vector()

        self.message_age = self.rcvdContent[88:92]
        self.rcvdFlags = self.rcvdContent[42:44]
        self.root_priority = self.rcvdContent[44:48]
        self.root_mac = self.rcvdContent[48:60]
        self.designated_bridge_priority = self.rcvdContent[68:72]
        self.designated_bridge_mac = self.rcvdContent[72:84]
        self.designated_bridge_port_id = self.rcvdContent[84:88]                    # PORT ID looks like 8001. Port priority+port_number. 80 == port priority (decimal 1-255). Port nr == 01
#        self.designated_bridge_port_id = self.rcvdContent[86:88]

        #int_path_cost = int(self.rcvdContent[60:68],16)+int(self.port_cost,16)

        int_path_cost = int(self.rcvdContent[60:68],16)+int(self.port_cost,16)
        str_path_cost = f'{int_path_cost:08x}'
        self.root_path_cost = str_path_cost
#        if(self.port_name=="rstp_2_7"):
#            print("HHHHHHHHHH assigned root path cost: "+self.root_path_cost)
#            print("HHHHHHHHHH rcvdContent[60:68]: "+self.rcvdContent[60:68])
#            print("HHHHHHHHHH self.port_cost"+self.port_cost)

        self.received_root_path_cost = self.rcvdContent[60:68]
        self.port_hello_time = self.rcvdContent[96:100]
        self.port_max_age = self.rcvdContent[92:96]
        self.port_forward_delay = self.rcvdContent[100:104]

        self.this_logger.log_string("update_port_priority_vector: "+self.root_priority+self.root_mac+self.received_root_path_cost+\
                self.designated_bridge_priority+self.designated_bridge_mac+self.designated_bridge_port_id+self.port_id+"(total cost:"+\
                self.root_path_cost+")")

        # If sender is root
#        if(self.this_bridge.root_pr_vector.root_mac == self.designated_bridge_mac):
#            for p in self.this_bridge.ports:
#                p.root_priority = self.designated_bridge_priority
            #self.this_bridge.root_pr_vector.root_priority = self.designated_bridge_priority
            #self.this_bridge.root_pr_vector.root_cost = self.port_cost

        # if this is root port
        if(self.this_bridge.root_pr_vector.root_port_id == self.port_id):
            self.this_bridge.update_root_pr_vector(self.port_id)
        self.rcvdInfoWhile = 0

    def reset_port_priority_vector(self):
        self.rcvdMsg = False            # 18thfeb
        self.rcvdContent = ""           # 18thfeb
        self.flags = helpers.set_binary_bit(helpers.strhex_to_bin(self.flags), 2, "0") # Forwarding: no/0
        self.flags = helpers.set_binary_bit(helpers.strhex_to_bin(self.flags), 3, "0") # Learning: no/0
        self.flags = helpers.set_binary_bit(helpers.strhex_to_bin(self.flags), 4, "1") # set Designated role flag (11): xxxx1xxx
        self.flags = helpers.set_binary_bit(helpers.strhex_to_bin(self.flags), 5, "1") # set Designated role flag (11): xxxxx1xx
        self.flags = helpers.set_binary_bit(helpers.strhex_to_bin(self.flags), 6, "1") # set Proposing flag : xxxxxx1x

        if(self.this_bridge.i_am_root):
            self.fdWhile = int(self.this_bridge.forward_delay[0:2],16)
        else:
#            self.fdWhile = int(self.this_bridge.root_port.port_forward_delay[0:2],16)
#            print("UUU I'm not root")
            root_port_id = int(self.this_bridge.root_pr_vector.root_port_id[2:4],16)
#            print("UUU root port id: "+ str(root_port_id))
            self.fdWhile = int(self.this_bridge.ports[root_port_id].port_forward_delay[0:2],16)

#        if(self.port_role != "Disabled"):
        if(self.portEnabled == True):
            if(self.port_role == "Backup"):
                self.port_state = "Learning"
            else:
                self.port_state = "Discarding"
            self.port_role = "Designated"
#            if(self.port_name == "rstp_0_0"):
#                print("SSSSSSSSSSSSSSSSSSSS port class")
        else:
            self.port_role = "Disabled"                   # when port role is Disabled, set state also Disabled
            self.port_state = "Disabled"
#            if(self.port_name == "rstp_0_0"):
#                print("OOOOOOOOOOOOOOOO port class")
        self.message_age = "0000"
        self.rrWhile = 0            # int(self.this_bridge.forward_delay,16)# equal to forward delay (802.1d-2004, section 17.17.7)
        self.rbWhile = 0            #int(self.this_bridge.hello_time,16)*2 # 2x of hello_time
        self.proposed = False
        self.fdWhile = int(self.this_bridge.forward_delay[0:2],16)# equal to forward delay
        self.root_priority = "ffff"
        self.root_mac = "ffffffffffff"
        self.designated_bridge_priority="ffff"
        self.designated_bridge_mac = "ffffffffffff"
        self.designated_bridge_port_id = "ffff"               # Port ID actually consists of x2 hex priority + x2 hex_port_number.
        self.root_path_cost = "00000000"
        self.received_root_path_cost = "00000000"
        self.agreed = False                 # agreed on proposal.
        self.synced = False
        self.proposed = False               #I've received proposal
        self.proposing = True               #I'm sending proposals
        #self.flags = "3c"                                   # Forwarding/learning/Designated

    def set_port_priority(self,var):
        if(var > 0 and var <=255):
            self.port_priority = str(f'{var:02x}')          #changed from str(f'{vr:01x}')
#            self.port_id = self.port_priority+str(f'{self.port_id:02x}')
            self.port_id = self.port_priority+str(f'{self.port_nr:02x}')
            #self.reset_port_priority_vector()
        else:
            print("incorrect value")

    def set_port_cost (self,var):
        if(var >=1 and var <=  200000000):
            self.port_cost = str(f'{var:08x}')

            if(self.port_role == "Root" or self.port_role == "Alternate"):                          #
                int_path_cost = int(self.received_root_path_cost,16)+int(self.port_cost,16)
                str_path_cost = f'{int_path_cost:08x}'
                self.root_path_cost = str_path_cost

            if(self.port_id == self.this_bridge.root_pr_vector.root_port_id):
                print("updating root_pr_vector")
                self.this_bridge.update_root_pr_vector(self.port_id)
            print("setting port cost to: "+self.port_cost)  #+" (hex: "+hex(self.port_cost))
        else:
            print("not correct value")

    def disconnect_port(self):
        if(self.peer_name!="None" and (self.peer_name.__contains__("rstp_"))):               # disconnect a peers port from another connection
            a=self.peer_port;
            a.reset_port_connectivity()
            a.reset_port_priority_vector()
            self.reset_port_connectivity()                       # reset peer port
            self.reset_port_priority_vector()
        if(self.peer_name != "None" and (not self.peer_name.__contains__("rstp_"))):                    # connected to external device
            self.reset_port_connectivity()                       # reset peer port
            self.reset_port_priority_vector()
            #self.peer_name = "None"
            #self.port_name = "rstp_"+str(self.this_bridge.bridge_nr)+"_"+str(self.port_nr)         #secrets.token_hex(2)   # random port name. binds to this virtual dummy network card name
#            print("ip link add "+self.port_name+" type dummy")
            os.system("ip link add "+self.port_name+" type dummy")
#            print("ip link set "+self.port_name+" up")
            os.system("ip link set "+self.port_name+" up")

    def reset_port_connectivity(self):
        #print("ip link del "+self.port_name)            # clean up before creating a dummy port.
        os.system("ip link del "+self.port_name+" 2>1")            # clean up before creating a dummy port.

        #print("ip link add "+self.port_name+" type dummy")
        os.system("ip link add "+self.port_name+" type dummy")

        #print("ip link set "+self.port_name+" up")
        os.system("ip link set "+self.port_name+" up")

        #print(self.peer_name+" peer name set to: None")
        self.peer_port = port
        self.peer_name = "None"

    def get_bpdu(self):
        stri = self.get_bpdu_str()
        try:
            stri = bytearray.fromhex(self.get_bpdu_str())
            return bytearray.fromhex(self.get_bpdu_str())
        except:
            print("error: stri: "+str(self.message))

    def get_bpdu_str(self):
        if(self.this_bridge.i_am_root):
            self.message = [RSTP_MULTICAST_DEST,self.this_bridge.bridge_mac,BPDU_LENGTH,DSASSP,PROTOCOL_ID,VERSION,self.bpdu_type,self.flags,self.this_bridge.bridge_priority,self.this_bridge.bridge_mac,"00000000",self.this_bridge.bridge_priority,self.this_bridge.bridge_mac,self.port_id,"0000",self.this_bridge.max_age,self.this_bridge.hello_time,self.this_bridge.forward_delay,self.this_bridge.version_1,self.this_bridge.version_2]
        else:
            while(self.rcvdMsg):                #if message received and port_priority_vector possibly being updated - wait
                pass
            root_port_nr = int(self.this_bridge.root_pr_vector.root_port_id[2:4],16)
            message_age_int = int(self.this_bridge.ports[root_port_nr].message_age[0:2],16)+1
            if(message_age_int>255):                 # not sure where this reaching limit
                print("error: port "+self.port_name+" vector message age reached 255 or over: "+str(message_age_int))
                message_age = "ff00"
            else:
                message_age = f'{message_age_int:02x}'+"00"
            self.message = [RSTP_MULTICAST_DEST,self.this_bridge.bridge_mac,BPDU_LENGTH,DSASSP,PROTOCOL_ID,VERSION,self.bpdu_type,self.flags,self.this_bridge.root_pr_vector.root_priority,self.this_bridge.root_pr_vector.root_mac,self.this_bridge.root_pr_vector.root_cost,self.this_bridge.bridge_priority,self.this_bridge.bridge_mac,self.port_id,message_age,self.this_bridge.ports[root_port_nr].port_max_age,self.this_bridge.ports[root_port_nr].port_hello_time,self.this_bridge.ports[root_port_nr].port_forward_delay,self.this_bridge.version_1,self.this_bridge.version_2]
        n = 20              # Length of message array.
        msg = ""
        for i in range(0,n):
            msg = msg+self.message[i]
        return msg
        #return "0180c20000005254aa1caabb0029424203000000000010015254aa1caabb0000000010015254aa1caabb80030000140002000f00000000" 

