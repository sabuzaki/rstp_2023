import threading
import time
import helpers_rstp_2023 as helpers
class port_role_transition_state_machine(threading.Thread):
    def __init__(self, this_bridge):
        self.this_bridge = this_bridge
        threading.Thread.__init__(self)
#        self.t = False

#    def t_terminate(self):
#        self.t = True
    # Tries to implement functionality of updtRolesTree() method from 802.1d-2004 specification section 17.21.25
    def run(self):
        #for i in self.this_bridge.ports
        while(1):
            if(self.this_bridge.shutdown):
                break
            self.this_bridge.set_root_priority_vector()
            root_port_nr = int(self.this_bridge.root_pr_vector.root_port_id[2:4],16)

            if(not self.this_bridge.i_am_root):             # If I'm not root bridge, all my ports are Designated or Backup
                self.this_bridge.assign_root_port()                      
                self.detect_alternate_port()

            # Either if I'm root or not root do following
            # Find Discarding ports or check Designated ports to be set 
            for i in self.this_bridge.ports:
                #if(self.this_bridge.i_am_root):
                self.detect_backup_port(i)                      # backup port state always == Discarding
                if(i.port_role=="Designated"):
                    self.update_designated_port_state(i)
            time.sleep(0.01)

    # When port is reset, it is always set to Deignated role. If another bridge connected to the same port,
    # and that switch priority is lower, it will send proposal flag, when received this bridge will send agreement
    # flag and will set variable of port object "agreed"=="True". This way it will transition immediately to "Forwarding"
    # state after agreement.
    # Otherwise: if agreed is set to False, wait until forward_delay timer (fdWhile) will reach 0, meanwhile maintainging "Discarding"
    # state. When reached 0 after 15 default seconds, transition to "Learning" and set fdWhile to 15 again. When that reached 0,
    # transition to "Forwarding" state.

    def update_designated_port_state(self,i):
        root_port_nr = int(self.this_bridge.root_pr_vector.root_port_id[2:4],16)
        if(i.agreed):
                i.flags = helpers.set_binary_bit(helpers.strhex_to_bin(i.flags), 6, "0") # Set Porposing flag to 0 xxxxxx0x
                i.flags = helpers.set_binary_bit(helpers.strhex_to_bin(i.flags), 2, "1") # Forwarding: Y/1 xx1xxxxx
                i.flags = helpers.set_binary_bit(helpers.strhex_to_bin(i.flags), 3, "1") # Learning: Y/1 xxx1xxxx
                i.proposing = False
                i.port_state="Forwarding"
        else:               # if not agreed
            # when port initializes it has fdWhile==forward_delay(15sec). it goes down every 1 second. when it reaches 0, if port role is 
            # designated, put it into Learning state. after 15 seconds change from learning to Forwarding.
            if(i.portfast==True):
                i.agreed = True
                i.synced = True
                i.flags = helpers.set_binary_bit(helpers.strhex_to_bin(i.flags), 2, "1") # set Forwarding: Y/1
                i.flags = helpers.set_binary_bit(helpers.strhex_to_bin(i.flags), 6, "0") # remove Porposing flag 
                i.proposing = False
            elif(i.fdWhile==0):                   #fdWhile == forward_delay variable (default 15), which is decremented every 1 second by timer class
                if(i.port_state=="Discarding"):
                    i.flags = helpers.set_binary_bit(helpers.strhex_to_bin(i.flags), 3, "1") # Learning: no/0
                    i.port_state="Learning"
                    if(self.this_bridge.i_am_root):
                        i.fdWhile= int(i.this_bridge.forward_delay[0:2],16)
                    else:
                        i.fdWhile= int(self.this_bridge.ports[root_port_nr].port_forward_delay[0:2],16)
                elif(i.port_state=="Learning"):
                    i.port_state="Forwarding"
#                    i.this_logger.log_string("PPPPPPPPPPPPPPP: set port state Forwarding")
                    i.flags = helpers.set_binary_bit(helpers.strhex_to_bin(i.flags), 2, "1") # set Forwarding: Y/1
                    i.flags = helpers.set_binary_bit(helpers.strhex_to_bin(i.flags), 6, "0") # remove Porposing flag 
                    i.agreed = True                         
                    i.synced = True
                    i.proposing = False

    # backup port state is always == "Discarding". If not detected that this is bacup port, do nothing (just log).
    # This function checks if the message_bridge_id is the same as this bridge. If so, check which port has lower ID (priority + port_nr),
    # one which has HIGHER id, transitions to role==Backup and state==Discarding
    def detect_backup_port(self,i):
        best_root_id = self.this_bridge.bridge_priority + self.this_bridge.bridge_mac
        #port_root_id = i.root_priority + i.root_mac
        message_bridge_id = i.designated_bridge_priority + i.designated_bridge_mac
        #if(i.rbWhile!=0 and (i.designated_bridge_port_id < i.port_id) and (message_bridge_id == self.this_bridge.bridge_id)):
        if((i.designated_bridge_port_id < i.port_id) and (message_bridge_id == self.this_bridge.bridge_id)):
            i.this_logger.log_string("message_check: received message from myself...portID is higher...set port role to \'Backup\'")
            i.flags = helpers.set_binary_bit(helpers.strhex_to_bin(i.flags), 2, "0") # Forwarding: no/0
            i.flags = helpers.set_binary_bit(helpers.strhex_to_bin(i.flags), 3, "0") # Learning: no/0
            i.flags = helpers.set_binary_bit(helpers.strhex_to_bin(i.flags), 4, "0") # set role bit flag as Bck/Alt: xxxx0xxx
            i.flags = helpers.set_binary_bit(helpers.strhex_to_bin(i.flags), 5, "1") # set role bit flag as Bck/Alt: xxxxx1xx
            i.flags = helpers.set_binary_bit(helpers.strhex_to_bin(i.flags), 5, "1") # set proposing flag as : xxxxxx1x
            i.port_role="Backup"
            i.port_state="Discarding"
        elif(i.designated_bridge_port_id > i.port_id and i.port_role == "Backup" and (message_bridge_id == self.this_bridge.bridge_id)):
            i.this_logger.log_string("resetting port from Backup to Designated")
            i.reset_port_priority_vector()

    def detect_alternate_port(self):
        root_port_nr = int(self.this_bridge.root_pr_vector.root_port_id[2:4],16)
        # Find alternate ports to be set
        for i in self.this_bridge.ports:
            # run for all ports but not root port. Select Alternate or Discarding. Default is Designated.
            if(i.port_nr!=root_port_nr and i.port_role != "Disabled"):
                best_root_id = self.this_bridge.root_pr_vector.root_priority+self.this_bridge.root_pr_vector.root_mac
                port_root_id = i.root_priority + i.root_mac
                message_bridge_id = i.designated_bridge_priority + i.designated_bridge_mac
                # If 
                if(i.fdWhile!=0 and \
                        (best_root_id == port_root_id) and \
                        (i.received_root_path_cost < self.this_bridge.ports[root_port_nr].root_path_cost) or \
                        (i.received_root_path_cost == self.this_bridge.ports[root_port_nr].root_path_cost  and \
                        message_bridge_id < self.this_bridge.bridge_id) and \
                        (message_bridge_id != self.this_bridge.bridge_id)):
                    if(i.port_role != "Alternate"):
                        self.set_alternate_port(i)
                else:  pass
                    #i.this_logger.log_string("port_role_transition_state_machine: did not set to Alternate port as my root path cost is lower: "+\
                    #        str(int(self.this_bridge.ports[root_port_nr].root_path_cost,16)))
                    # Missing functionality!!!!! 

    def set_alternate_port(self,i):
        i.port_role="Alternate"             
        i.port_state="Discarding"                 # Alternate port is always in blocking state.
        i.flags = helpers.set_binary_bit(helpers.strhex_to_bin(i.flags), 2, "0") # forwarding: no/0
        i.flags = helpers.set_binary_bit(helpers.strhex_to_bin(i.flags), 3, "0") # learning: no/0
        i.flags = helpers.set_binary_bit(helpers.strhex_to_bin(i.flags), 4, "0") # set role bit flag as Bck/Alt: xxxx0xxx
        i.flags = helpers.set_binary_bit(helpers.strhex_to_bin(i.flags), 5, "1") # set role bit flag as Bck/Alt: xxxxx1xx
        i.flags = helpers.set_binary_bit(helpers.strhex_to_bin(i.flags), 5, "1") # set proposing flag as : xxxxxx1x
        i.this_logger.log_string("port_role_transition_state_machine: port set to role \'Alternate\'.")
        i.proposing = False
        i.agreed = True                         # No proposal/agreement between bridges which deciding which port is alternate.
                                                # thus agreed variable always true when port is Alternate

