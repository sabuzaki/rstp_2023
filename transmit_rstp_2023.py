import threading
import time
ETH_P_ALL = 0x0003
class port_transmit_state_machine(threading.Thread):
    def __init__(self,this_port,sckt):
        self.this_port = this_port
        self.sckt = sckt
        threading.Thread.__init__(self)

    def run(self):
        self.this_port.this_logger.log_string("Sending for port :" + str(self.this_port.port_name))
        while(1):
            if(self.this_port.this_bridge.shutdown):
                break
            role = self.this_port.port_role
            self.this_port.this_logger.log_string("port_transmit_state_machine: Port role: "+self.this_port.port_role+"; Agreed: "+str(self.this_port.agreed))

            if(((role=="Root") and (self.this_port.agreed!=True))\
                    or (self.this_port.this_bridge.tcWhile>0)
                    or role=="Designated"):
                bpdu_str = self.this_port.get_bpdu_str()
                bpdu = self.this_port.get_bpdu()
#                if(not self.this_port.operEdge and self.this_port.portEnabled):
                if(self.this_port.port_type!="Edge" and self.this_port.portEnabled):
                    try:
                        #if(self.this_port.port_name=="rstp_1_1"):
                        #    print("transmitting for port: rstp_1_1")
                        if(self.this_port.peer_name!="None"):
                            self.sckt.bind((self.this_port.peer_name, ETH_P_ALL))
                        else:
                            self.sckt.bind((self.this_port.port_name, ETH_P_ALL))
                        sendbytes = self.sckt.send(bpdu)
                        self.this_port.this_logger.log_string("SENT: "+bpdu_str)
                        self.this_port.txHoldCount += 1
                    except:
                       self.this_port.this_logger.log_string("port_transmit_state_machine: failed to bind to network card...Will re-try")
            if(self.this_port.this_bridge.i_am_root):
                #if(self.this_port.this_bridge.tcWhile != 0 and self.this_port.txHoldCount <= 5 and self.this_port.agreed == False):           # tcWhile is set to 3xhello_time when topology change detected. txHoldCount is limit of BPDUs per second
                #    pass
                #else: time.sleep(int(self.this_port.this_bridge.hello_time[0:2],16))                # sleep for amout of bridge.hello_time
                time.sleep(int(self.this_port.this_bridge.hello_time[0:2],16))                # sleep for amout of bridge.hello_time
            else:
                #if(self.this_port.this_bridge.tcWhile != 0 and self.this_port.txHoldCount <= 5 and self.this_port.agreed == False):           # tcWhile is set to 3xhello_time when topology change detected. txHoldCount is limit of BPDUs per second
                #    pass
                #else: 
                root_port_nr = int(self.this_port.this_bridge.root_pr_vector.root_port_id[2:4],16)
                time.sleep(int(self.this_port.this_bridge.ports[root_port_nr].port_hello_time[0:2],16)) # sleep for amount of another root bridge hello_time
