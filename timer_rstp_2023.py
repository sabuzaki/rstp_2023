import threading
import time
import helpers_rstp_2023 as helpers
class port_timer_state_machine(threading.Thread):
    def __init__(self,this_bridge):
        self.ports = this_bridge.ports
        self.this_bridge = this_bridge
        threading.Thread.__init__(self)

    def run(self):
#        time.sleep(3)               # Allow time for initialization
        while(1):
            if(self.this_bridge.shutdown):
                break
            for i in self.ports:
                i.tick = True
#                if(i.port_name=="rstp_1_1"):
#                    timestamp = str(datetime.now().hour)+":"+str(datetime.now().minute)+":"+str(datetime.now().second)
#                    print("SSSSSSSSSSS: "+timestamp+" "+str(i.rcvdInfoWhile))
#                if(i.rcvdInfoWhile!=0):                             #
#                    i.rcvdInfoWhile=i.rcvdInfoWhile-1             # rcvdInfoWhile - how long passed since superior or root BPDU was received on that port.
                i.rcvdInfoWhile+=1
               #     i.this_logger.log_string("7878 port_timer_state_machine: rcvdInfoWhile: "+str(i.rcvdInfoWhile))
#                i.this_logger.log_string("port_timer_state_machine: rcvdInfoWhile: "+str(i.rcvdInfoWhile))

                if(i.rrWhile!=0):
                    i.rrWhile = i.rrWhile-1

                if(i.rbWhile!=0):           # used by Backup port. Every time Backup port receives that same BPDU but from same bridge superior port, resets value to forward_delay (15sec)
                    i.rbWhile = i.rbWhile-1

                if(i.fdWhile!=0):           # used by Alternate port. Every time Alternate port receives that superior BPDU, it resets this value to forward_delay (15sec)
                    i.fdWhile = i.fdWhile-1

                i.txHoldCount = 0           # incremented each time BPDU is sent. Current maximum BPDUs per second is 30

            if(self.this_bridge.tcWhile!=0):
                self.this_bridge.tcWhile -= 1
            elif(self.this_bridge.tc==True):                # If tcWhile reached zero and tc still True, end the Topology change and change flags in all ports
                self.this_bridge.tc=False
                for p in self.this_bridge.ports:
                    p.flags = helpers.set_binary_bit(helpers.strhex_to_bin(p.flags), 7, "0") # set TCN flag xxxxxxx1

            self.this_bridge.tcSince += 1        # since when topology changed in seconds

            time.sleep(1)       # tick machine. 
