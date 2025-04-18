# howdy2023
import secrets
from datetime import datetime
import netifaces                                    # needed by cleanup_and_exit()
from os import listdir                              # needed by print_physical_interfaces
from os.path import islink, realpath, join         # needed by print_physical_interfaces
import os
import time
import random
import numpy as np
import pygraphviz as pgv

#from rstp_2023 import bridge

PORTS_PER_BRIDGE = 4
#from rstp_2023 import bridge

def print_physical_interfaces():

    interfaces = [i for i in listdir("/sys/class/net") if islink(join("/sys/class/net", i))]
    #interfaces = [i for i in interfaces if not realpath(join("/sys/class/net", i)).startswith(("/sys/devices/virtual", "/sys/devices/vif"))]
    interfaces2 = []
    for i in interfaces:
        if(i.__contains__("eth") or i.__contains__("ens") or i.__contains__("rstp_hub_")):
            interfaces2.append(i)

    #print("Physical interfaces:", str(interfaces))
    for i in interfaces2:
        print(i)


def get_physical_interfaces():
    interfaces = [i for i in listdir("/sys/class/net") if islink(join("/sys/class/net", i))]
    interfaces2 = []
    for i in interfaces:
#        if(i.__contains__("eth") or i.__contains__("ens")):
        if(i.__contains__("eth") or i.__contains__("ens") or i.__contains__("rstp_hub_")):
#        if(i.__contains__("eth")):
            interfaces2.append(i)
    #interfaces = [i for i in interfaces if not realpath(join("/sys/class/net", i)).startswith(("/sys/devices/virtual", "/sys/devices/vif"))]
    return interfaces2

#def generate_mac():                #  original
def generate_mac(nr):               # temporarily.
        #return "aabbccddee0"+str(nr)            # temporarily
        return "5254aabb" + secrets.token_hex(2)     # original. assign random ending to mac: 5254aabbccXX <XX as random>


def cleanup_and_exit(bridges):

    all_faces = netifaces.interfaces()
    for i in all_faces:
        if(i.__contains__("rstp_")):
            print("Deleting virtual network device "+i+"...")
            os.system("ip link del "+i)
    os._exit(os.EX_OK)

def format_bpdu_to_string_for_logs(bpdu):
        flags = helpers.strhex_to_bin((bpdu[42:44]))
        return "Dest:"+bpdu[0:12]+"|Src:"+bpdu[12:24]+"|Proto_id:"+bpdu[34:38]+"|Ver:"+bpdu[38:40]+"|Type:"+bpdu[40:42]+\
        "|FLAGS(bin):TCN-"+flags[0]+";AGR-"+flags[1]+";FRW-"+flags[2]+";LRN-"+flags[3]+";RLE-"+flags[4]+flags[5]+";PRP-"+flags[6]+";TCA-"+flags[7]\
        +"|Root_priority:"\
        +bpdu[44:48]+"|Root MAC:"+bpdu[48:60]+"|Path cost:\
        "+bpdu[60:68]+"|Bridge_priority:"+bpdu[68:72]+"|Bridge MAC:"+bpdu[72:84]+"|Root Port:"+bpdu[84:88]\
        +"|Message Age:"+bpdu[88:92]+"|Max Age:"+bpdu[92:96]+"|Hello Time:"+bpdu[96:100]+"|Forward Delay:\
        "+bpdu[100:104]+"|Version 1:"+bpdu[104:106]+"|Version 2:"+bpdu[106:110]
def generate_example_topology(bridges,bridge,topology_nr):

    for b1 in bridges:
        for p1 in b1.ports:
            p1.disconnect_port()
    if(topology_nr==1):
        while(len(bridges)<4):
            add_bridge(bridges,bridge)
        while(len(bridges)>4):
            pop_bridge(bridges)
        bridges[0].set_bridge_priority(int(28672))            ## set_bridge_priority module will check if correct value
        bridges[0].connect_port_to_port(0,bridges[1].ports[0])
        bridges[1].connect_port_to_port(1,bridges[2].ports[0])
        bridges[2].connect_port_to_port(1,bridges[3].ports[0])
        bridges[3].connect_to_network_card(1,"rstp_hub_0")
        bridges[3].connect_to_network_card(2,"rstp_hub_0")
    if(topology_nr==2):
        while(len(bridges)<3):
            add_bridge(bridges,bridge)
        while(len(bridges)>3):
            pop_bridge(bridges)
        bridges[2].set_bridge_priority(int(28672))            ## set_bridge_priority module will check if correct value
        bridges[2].connect_port_to_port(0,bridges[1].ports[0])
        bridges[1].connect_port_to_port(1,bridges[0].ports[4])
        bridges[0].connect_port_to_port(5,bridges[1].ports[7])
    if(topology_nr==3):
        bridges[0].set_bridge_priority(int(28672))            ## set_bridge_priority module will check if correct value
        while(len(bridges)<4):
            add_bridge(bridges,bridge)
        while(len(bridges)>4):
            pop_bridge(bridges)
        bridges[0].connect_port_to_port(0,bridges[1].ports[0])
        bridges[0].connect_port_to_port(1,bridges[2].ports[0])
        bridges[2].connect_port_to_port(1,bridges[1].ports[1])
        bridges[2].connect_port_to_port(2,bridges[3].ports[0])
        bridges[2].connect_port_to_port(3,bridges[3].ports[1])
    if(topology_nr==4):
        while(len(bridges)<3):
            add_bridge(bridges,bridge)
        while(len(bridges)>3):
            pop_bridge(bridges)
        bridges[0].connect_port_to_port(0,bridges[1].ports[0])
        bridges[0].set_bridge_priority(int(28672))            ## set_bridge_priority module will check if correct value
        bridges[0].connect_port_to_port(0,bridges[1].ports[0])
        bridges[0].connect_port_to_port(1,bridges[2].ports[0])
        bridges[1].connect_to_network_card(1,"rstp_hub_0")
        bridges[2].connect_to_network_card(1,"rstp_hub_0")
        bridges[2].connect_to_network_card(2,"rstp_hub_0")

    if(topology_nr==5):
        bridges[0].set_bridge_priority(int(28672))            ## set_bridge_priority module will check if correct value
        bridges[0].connect_port_to_port(0,bridges[1].ports[0])
    if(topology_nr==6):
        bridges[0].set_bridge_priority(int(24576))            ## set_bridge_priority module will check if correct value
        bridges[1].set_bridge_priority(int(61440))            ## set_bridge_priority module will check if correct value
        bridges[2].set_bridge_priority(int(28672))            ## set_bridge_priority module will check if correct value
        bridges[0].connect_port_to_port(0,bridges[1].ports[0])
        bridges[1].connect_port_to_port(4,bridges[2].ports[0])
    if(topology_nr==7):
        bridges[0].set_bridge_priority(int(28672))            ## set_bridge_priority module will check if correct value
        bridges[2].set_bridge_priority(int(36864))            ## set_bridge_priority module will check if correct value
        bridges[0].connect_port_to_port(0,bridges[1].ports[0])
        bridges[1].connect_port_to_port(4,bridges[2].ports[0])
    if(topology_nr==8):
        while(len(bridges)<3):
            add_bridge(bridges,bridge)
        while(len(bridges)>3):
            pop_bridge(bridges)
        bridges[0].set_bridge_priority(int(28672))            ## set_bridge_priority module will check if correct value
        bridges[1].set_bridge_priority(int(61440))            ## set_bridge_priority module will check if correct value
        bridges[2].set_bridge_priority(int(61440))            ## set_bridge_priority module will check if correct value
        bridges[0].connect_port_to_port(0,bridges[1].ports[0])
        bridges[1].connect_port_to_port(1,bridges[2].ports[0])
        bridges[2].connect_port_to_port(1,bridges[3].ports[0])
        bridges[3].connect_to_network_card(1,"rstp_hub_0")
    if(topology_nr==9):
        while(len(bridges)<5):
            add_bridge(bridges,bridge)
        while(len(bridges)>5):
            pop_bridge(bridges)
        bridges[0].set_bridge_priority(int(28672))            ## set_bridge_priority module will check if correct value
        bridges[1].set_bridge_priority(int(61440))            ## set_bridge_priority module will check if correct value
        bridges[2].set_bridge_priority(int(61440))            ## set_bridge_priority module will check if correct value
        bridges[3].set_bridge_priority(int(61440))            ## set_bridge_priority module will check if correct value
        bridges[0].connect_port_to_port(0,bridges[1].ports[0])
        bridges[1].connect_port_to_port(1,bridges[2].ports[0])
        bridges[2].connect_port_to_port(1,bridges[3].ports[0])
        bridges[3].connect_port_to_port(1,bridges[4].ports[0])
    # topology which was extensively used to troubleshoot final stages of "increasing bridge priority" defect. Loop is being created (50% of times) when increased root bridge priority
    if(topology_nr==10):
        while(len(bridges)<7):
            add_bridge(bridges,bridge)
        while(len(bridges)>7):
            pop_bridge(bridges)
        bridges[0].set_bridge_priority(int(28672))            ## 
        bridges[0].connect_port_to_port(0,bridges[1].ports[0])
        bridges[1].connect_port_to_port(1,bridges[2].ports[0])
        bridges[2].connect_port_to_port(1,bridges[3].ports[0])
        bridges[2].connect_port_to_port(7,bridges[3].ports[7])
        bridges[3].connect_port_to_port(1,bridges[4].ports[0])
        bridges[4].set_bridge_priority(int(28672))            ##
        bridges[4].connect_port_to_port(1,bridges[5].ports[0])
        bridges[5].connect_port_to_port(1,bridges[6].ports[0])
        bridges[6].connect_port_to_port(7,bridges[0].ports[7])
        bridges[6].connect_to_network_card(6,"rstp_hub_0")
        bridges[6].connect_to_network_card(1,"rstp_hub_0")

#        bridges[6].connect_port_to_port(1,bridges[7].ports[0])
#        bridges[7].connect_port_to_port(1,bridges[8].ports[0])
#        bridges[8].connect_port_to_port(1,bridges[0].ports[1])
    if(topology_nr==11):
        print("\nStaring Topology 11...")
        while(len(bridges)<7):
            add_bridge(bridges,bridge)
        while(len(bridges)>7):
            pop_bridge(bridges)
        bridges[0].set_bridge_priority(int(28672))            ## 
        bridges[0].connect_port_to_port(0,bridges[1].ports[0])
        bridges[1].connect_port_to_port(1,bridges[2].ports[0])
        bridges[2].connect_port_to_port(1,bridges[3].ports[0])
        bridges[3].connect_port_to_port(1,bridges[4].ports[0])
        bridges[4].set_bridge_priority(int(28672))            ##
        bridges[4].connect_port_to_port(1,bridges[5].ports[0])
        bridges[5].connect_port_to_port(1,bridges[6].ports[0])
        bridges[6].connect_port_to_port(1,bridges[0].ports[1])
        bridges[6].ports[6].peer_name="rstp_hub_0"
        bridges[6].ports[7].peer_name="rstp_hub_0"
        bridges[5].ports[2].peer_name="rstp_hub_0"

def generate_random_topology(bridges,ports_to_connect):
#    print("Connectivity percentage is "+str(percentage)+"%.") 
#    percentage = percentage * 0.01
    bl = len(bridges)
    all_skip = []
    for b1 in bridges:
        for p1 in b1.ports:
            p1.disconnect_port()

    for b1 in bridges:
        print("current connections:")
        for p in b1.ports:
            print(p.port_name+":"+p.peer_name)
        pl = len(b1.ports)
#        nr_to_connect = round(pl * ports)
        nr_to_connect = ports_to_connect
        print("Connecting "+str(nr_to_connect)+" ports of Bridge-"+str(b1.bridge_nr))
        p1_skip = []
        while(nr_to_connect):
            if(check_if_all_bridge_ports_connected(b1) != True):
                p1 = random.randrange(0,pl)
                while([b1.bridge_nr,p1] in all_skip):
                    p1 = random.randrange(0,pl)
                b2 = random.randrange(0,bl)
                p2 = random.randrange(0,pl)
                while([b2,p2] in all_skip or (b2==b1.bridge_nr)):
                    b2 = random.randrange(0,bl)
                    p2 = random.randrange(0,pl)
                print("Connecting "+b1.ports[p1].port_name+" -> "+bridges[b2].ports[p2].port_name)
                b1.connect_port_to_port(p1,bridges[b2].ports[p2])
                all_skip.append([b2,p2])
                all_skip.append([b1.bridge_nr,p1])
                p1_skip.append([p1])
                nr_to_connect = nr_to_connect - 1
            else:
                print("aborting.....all ports connected")
                nr_to_connect = 0

def create_hub(nr):
    os.system("ip link del rstp_hub_"+str(nr))            # clean up before creating a dummy port.
    os.system("ip link add rstp_hub_"+str(nr)+" type dummy")
    os.system("ip link set rstp_hub_"+str(nr)+" up")

def check_if_all_bridge_ports_connected(br):
    r = True
    for p in br.ports:
        if(p.peer_name == "None"):
            r = False
    return r

def generate_graphviz(bridges,just_image):
        already_created = []
        n = "\n"           # once
        nn = "\\n"        # once
#        nn = "\\\\n"
        graph = ""
        #print("digraph G {\nnode [shape=record];\nnewrank=True;\nrankdir=TB;\nranksep=2;\n")
        graph += "digraph G {\nlabel=\"Known major defects:increasing priority of a root bridge\"\nnode [shape=record];\nnewrank=True;\nrankdir=TB;\nranksep=1.2;\n"
        lb = len(bridges)-1
        for b in range(0,lb):
                #print("BR"+str(b)+":rstp_"+str(b)+"_1->BR"+str(b+1)+":rstp_"+str(b+1)+"_1 [style=invis];")
                graph += "BR"+str(b)+":rstp_"+str(b)+"_1->BR"+str(b+1)+":rstp_"+str(b+1)+"_1 [style=invis];\n"
                
        #print("BR"+str(lb)+":rstp_"+str(b+1)+"_1->HB0[style=invis];")
        graph += "BR"+str(lb)+":rstp_"+str(b+1)+"_1->HB0[style=invis];\n"

        for b in bridges:
            bn = str(b.bridge_nr)
            bp = str(b.bridge_priority)
            bm = str(b.bridge_mac[0:2]+":"+b.bridge_mac[2:4]+":"+b.bridge_mac[4:6]+":"+b.bridge_mac[6:8]+":"+b.bridge_mac[8:10]+":"+b.bridge_mac[10:12])
            if(b.i_am_root): 
                rpc = str(0)
            else:
                root_port_nr = int(b.root_pr_vector.root_port_id[2:4],16)
                rpc = str(int(b.ports[root_port_nr].root_path_cost,16))
            #print("subgraph cluster_"+bn+" {{ {0}label=\"Bridge".format(n)+bn+nn+bp+"."+bm+" best path cost: "+rpc+"\";\nrank=same;")
            graph += "subgraph cluster_"+bn+" {{ {0}label=\"Bridge".format(n)+bn+nn+bp+"."+bm+" best path cost: "+rpc+"\";\nrank=same;\n"
            if(b.i_am_root): 
                #print("bgcolor=pink;")
                graph += "bgcolor=pink;\n"
            lp = len(b.ports)
#            tmp_str = "BR"+bn+"[label=\"<rstp_"+bn+"_"
            tmp_str = "BR"+bn+"[label=\""
            for index, p in enumerate(b.ports):
                pn = str(p.port_nr)
                pr = str(p.port_role[0:3])
                pc = str(int(p.port_cost,16))
                pri = str(int(p.port_priority,16))
                tmp_str += "<rstp_"+bn+"_"+pn+">Port"+pn+nn+pr+nn+"Cost: "+pc+nn+"Pri:"+pri+nn
#                print("rstp_"+bn+"_"+pn+"[label=\"port"+pn+nn+pr+nn+"cost: "+pc+nn+Prior: "+pri+"\"];")
                if(lp!=index):
                    tmp_str += "|"
#                    print("rstp_"+bn+"_"+pn+"->rstp_"+bn+"_"+str(p.port_nr+1)+"[style=invis];")
                #tmp_str = "BR"+bn+"[label=\"<rstp_"+bn+"_"
            tmp_str += "\"];"
            #print(tmp_str)
            graph += tmp_str
            #print("}")
            graph += "}"+n
        # Generate HUB. Only one is possible at this time
        #print("subgraph cluster_99 {\nlabel=\"LOCAL HUB\"\nHB0[label=\"<a>Port1|<b>Port2|<c>Port3|...|...|...\";width=8]\n}")
        graph += "subgraph cluster_99 {\nlabel=\"LOCAL HUB\"\nHB0[label=\"<a>Port1|<b>Port2|<c>Port3|...|...|...\";width=8]\n}\n"

        for bn,b in enumerate(bridges):
            for p in b.ports:
        #        if(p.peer_name != "None" and (not p.peer_name.__contains__("rstp_"))):                    # connected to external device
                if(p.peer_name != "None" and (not p.peer_name.__contains__("rstp_"))): # connected to external device
                    #print("BR"+str(bn)+":rstp_"+str(p.this_bridge.bridge_nr)+"_"+str(p.port_nr)+" ->"+p.peer_name+" [arrowhead=none];")
                    graph += "BR"+str(bn)+":rstp_"+str(p.this_bridge.bridge_nr)+"_"+str(p.port_nr)+" ->"+p.peer_name+" [arrowhead=none];\n"
                elif(p.peer_name != "None" and p.peer_name.__contains__("rstp_hub")):
                    if(p.port_role == "Backup"):
                        graph += "BR"+str(bn)+":"+p.port_name+" -> "+"HB0 [arrowhead=none,style=dashed];\n"
                    else:
                        graph += "BR"+str(bn)+":"+p.port_name+" -> "+"HB0 [arrowhead=none];\n"
                elif(p.peer_name != "None" and (p.peer_name not in already_created)):
                    peer_bridge_nr = p.peer_port.this_bridge.bridge_nr
                    #print("BR"+str(bn)+":"+p.port_name+" -> "+"BR"+str(peer_bridge_nr)+":"+p.peer_name+" [arrowhead=none];")
                    if(p.port_role=="Root" or p.peer_port.port_role=="Root"):
                        graph += "BR"+str(bn)+":"+p.port_name+" -> "+"BR"+str(peer_bridge_nr)+":"+p.peer_name+" [arrowhead=none,style=bold];\n"
#                    elif(p.port_role=="Alternate" or p.peer_port.port_role=="Alternate" or p.port_role=="Backup" or p.peer_port.port_role=="Backup"):
                    elif(p.port_role=="Alternate" or p.peer_port.port_role=="Alternate"):
                        graph += "BR"+str(bn)+":"+p.port_name+" -> "+"BR"+str(peer_bridge_nr)+":"+p.peer_name+" [arrowhead=none,style=dashed];\n"
                    else:
                        graph += "BR"+str(bn)+":"+p.port_name+" -> "+"BR"+str(peer_bridge_nr)+":"+p.peer_name+" [arrowhead=none];\n"
                    already_created.append(p.port_name)
#        print("}")
#        print("")
#        print("Paste above graph code to:     http://magjac.com/graphviz-visual-editor/")

        graph += "}\n"
        graph += "\n"
        if(just_image):                  # if image set to true, just export and do not display output of a graph to cli
            G = pgv.AGraph(graph)
            G.layout('dot')
            G.draw('rstp_graph.png')
        else:
            G = pgv.AGraph(graph)
            G.layout('dot')
            G.draw('rstp_graph.png')
            graph += "Paste above graph to:     http://magjac.com/graphviz-visual-editor/\n"
            graph += "OR open rstp_graph.png with image viewer. rstp_graph.png is updated every time option 45 is used. Most image viewers will refresh it automatically."
            print(graph)

def show_traffic_stats():
        os.system("cat /proc/net/dev")

def strbin_to_hex(var):
    if(len(var) == 8):
        return "{0:0>2x}".format(int(var,2))
    else:
        return "accepting only 8 bits in string to convert"

def strhex_to_bin(var):
    if(len(var) == 2):
        return str("{0:08b}".format(int(var,16)))
    else:
        return "accepting only 2 hex values (8 bits)"

def set_binary_bit(bin_str,nr,val):                  #nr = bit position left-to-right (0-7). hx-> 8 bit values.ie: 01010101. val->value(1 or 0n)
    bin_str = bin_str[:nr] + val + bin_str[nr+1:]
    return '%02x' % int(bin_str, 2)

def add_bridge(bridges,bridge):
    l = len(bridges)
    bridges.append(bridge(l,generate_mac(l),len(bridges[0].ports)))     # temp
#    bridges.append(bridge(l,generate_mac(),len(bridges[0].ports)))     # original

# Do not use. Not recommended. When having bridges 1-4 and bridge 2 deleted there might be issues generating topologies or other....
def terminate_bridge(bridges,bridge_nr):
    bridges[bridge_nr-1].shutdown = True
    print("Shutting down Bridge"+str(bridge_nr)+"....please wait")
    time.sleep(2)
    del bridges[bridge_nr-1]

def pop_bridge(bridges):
    nr = len(bridges)-1     # disconnect all ports from last bridge
    for p in bridges[nr].ports:
        p.disconnect_port()
    bridges.pop()

def get_number(string,maximum):
    nr = input(string+str(maximum)+": ")
    if(nr.isnumeric()):
        if(int(nr)>=0 and int(nr)<=maximum):
            return int(nr)
        else:
            return -1
    else:
            return -1

class logger():

    def __init__(self):
        self.all_logs = []

    def log_string(self,string):
        timestamp = str(datetime.now().hour)+":"+str(datetime.now().minute)+":"+str(datetime.now().second)
        self.all_logs.append(timestamp+" "+string)
        if(len(self.all_logs)>250):                 # remove some of the logs once reached 150 size
            self.all_logs = self.all_logs[-200:]


    # bpdu is a message received represented in string. Append is what to append before a log (i.e: SENT or RECV)
    def log_bpdu(self,bpdu, append):
        flags = strhex_to_bin((bpdu[42:44]))
        timestamp = str(datetime.now().hour)+":"+str(datetime.now().minute)+":"+str(datetime.now().second)
        self.all_logs.append(timestamp+"|"+append+"Dest:"+bpdu[0:12]+"|Src:"+bpdu[12:24]+"|Proto_id:"+bpdu[34:38]+"|Ver:"+bpdu[38:40]+"|Type:"+bpdu[40:42]+\
        #print(append+"Dest:"+bpdu[0:12]+"|Src:"+bpdu[12:24]+"|Proto_id:"+bpdu[34:38]+"|Ver:"+bpdu[38:40]+"|Type:"+bpdu[40:42]+\
        "|FLAGS(bin):TCN-"+flags[0]+";AGR-"+flags[1]+";FRW-"+flags[2]+";LRN-"+flags[3]+";RLE-"+flags[4]+flags[5]+";PRP-"+flags[6]+";TCA-"+flags[7]\
        +"|Root_priority:"\
        +bpdu[44:48]+"|Root MAC:"+bpdu[48:60]+"|Path cost:\
        "+bpdu[60:68]+"|Bridge_priority:"+bpdu[68:72]+"|Bridge MAC:"+bpdu[72:84]+"|Sending Port:"+bpdu[84:88]\
        +"|Message Age:"+bpdu[88:92]+"|Max Age:"+bpdu[92:96]+"|Hello Time:"+bpdu[96:100]+"|Forward Delay:\
        "+bpdu[100:104]+"|Version 1:"+bpdu[104:106]+"|Version 2:"+bpdu[106:110])
        #print("pop: "+self.all_logs.pop())

        if(len(self.all_logs)>250):                 # remove some of the logs once reached 100 size
            self.all_logs = self.all_logs[-200:]

    def print_logs(self):
        for i in self.all_logs:
            print(i)
        print("Log size: "+str(len(self.all_logs)))

