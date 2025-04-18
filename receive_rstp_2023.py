import threading
import time

ETH_P_ALL = 0x0003
BUFFER_SIZE = 65536

class port_receive_state_machine(threading.Thread):
    def __init__(self, this_port, sckt):
        self.this_port = this_port
        self.sckt = sckt
        threading.Thread.__init__(self)


    def run(self):
        self.this_port.rcvdBPDU = True
        while(1):
            if(self.this_port.this_bridge.shutdown):
                break
            try:
                if(self.this_port.peer_name != "None"):
                    self.sckt.bind((self.this_port.peer_name, ETH_P_ALL))
                else:
                    self.sckt.bind((self.this_port.port_name, ETH_P_ALL))
#                if((not self.this_port.operEdge) and self.this_port.portEnabled):
                if(self.this_port.port_type!="Edge" and self.this_port.portEnabled):
                    buffer=self.sckt.recvfrom(BUFFER_SIZE)[0].hex()
                    if(buffer[0:12]=="0180c2000000"):               # RSTP multicast destination
#                        if(self.this_port.port_name=="ens3"):
#                            print("received RSTP on ens3 NNNNNNNN")
#                        self.this_port.this_logger.log_string("RECV: "+buffer)
                        #self.this_port.this_logger.log_bpdu(buffer, "RECV: ")
    #                        print(buffer)
                        self.this_port.rcvdContent = buffer
                        self.this_port.rcvdMsg = True
                    else:
                        self.this_port.this_logger.log_string("RECV: NOT RSTP: "+buffer)
                else:
                    self.this_port.this_logger.log_string("port_receive_state_machine: port is edge or not enabled....sleeping 2...")
                    time.sleep(2)
                buffer = BUFFER_SIZE * 0
            except:
                self.this_port.this_logger.log_string("port_receive_state_machine: Failed to bind to network card..Will re-try.")
                time.sleep(2)
