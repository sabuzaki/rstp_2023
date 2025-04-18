#test
import helpers_rstp_2023 as helpers
from bridge_rstp_2023 import bridge
#from rstp_2023 import bridge
import tabulate                 # must me installed: pip install tabulate

MAX_AGE_STATIC = 20
MAX_FORWARD_DELAY_STATIC = 20       # integer
MAX_HELLO_TIME_STATIC = 20          # integer
MAX_FORWARD_DELAY_STATIC = 20       # integer
PORTS_PER_BRIDGE = 8
PORT_PRIORITY_MAX = 255

class cli_menu():
    def print_all_bridge_connections(self,bridges):
        for b in bridges:
            for p in b.ports:
                print("Bridge"+str(b.bridge_nr)+" port"+str(p.port_nr)+" (int:"+p.port_name+") connected to: "+p.peer_name)

    #def get_number(string,maximum):
    #    nr = input(string+str(maximum)+": ")
    #    if(nr.isnumeric()):
    #        if(int(nr)>=1 and int(nr)<=maximum):
    #            return int(nr)
    #        else:
    #            return 0
    #    else:
    #            return 0
    def print_bridge_status(self,br):
        if(br.i_am_root):
            print(" ################## Bridge-"+str(br.bridge_nr)+" ####################")
            print("\n Root ID:    Priority    "+str(int(br.bridge_priority,16)))
            print("             Address     "+br.bridge_mac[0:4]+"."+br.bridge_mac[4:8]+"."+br.bridge_mac[8:12])
            print("             This bridge is the root")
            print("             Hello Time  "+str(int(br.hello_time[0:2],16))+" sec Max Age "+\
                    str(int(br.max_age[0:2],16))+"  sec Forward Delay "+str(int(br.forward_delay[0:2],16))+" sec")
        else:
            root_port_nr = int(br.root_pr_vector.root_port_id[2:4],16)
#            print("\n Root ID:    Priority    "+str(int(br.root_port.root_priority,16)))
            print("\n Root ID:    Priority    "+str(int(br.root_pr_vector.root_priority,16)))
            print("             Address     "+br.root_pr_vector.root_mac[0:4]+"."+br.root_pr_vector.root_mac[4:8]+"."+br.root_pr_vector.root_mac[8:12])
            print("             Cost        "+str(int(br.root_pr_vector.root_cost,16)))
            print("             Port        "+str(int(br.root_pr_vector.root_port_id[2:4],16)))
            print("              Hello Time   "+str(int(br.ports[root_port_nr].port_hello_time[0:2],16))+" sec  Max Age "+\
                    str(int(br.ports[root_port_nr].port_max_age[0:2],16))+"  sec Forward Delay "\
                    +str(int(br.ports[root_port_nr].port_forward_delay[0:2],16))+" sec")
        print("")
        print(" Bridge ID:  Priority    "+str(int(br.bridge_priority,16)))  
        print("             Address     "+br.bridge_mac[0:4]+"."+br.bridge_mac[4:8]+"."+br.bridge_mac[8:12])
        print("             Hello Time  "+str(int(br.hello_time[0:2],16))+" sec Max Age "+\
                str(int(br.max_age[0:2],16))+"  sec Forward Delay "+str(int(br.forward_delay[0:2],16))+" sec")
#        print("             Aging Time  <unknown>")
        print("             Topology changed times "+str(br.tcCounter))
        print("             Topology change since  "+str(br.tcSince))
        print("             tcWhile counter        "+str(br.tcWhile))
        print("")
#        headers = ['Inter-\nface','Role','Status', 'Cost', 'Cost\ntow-\nards\nroot','Prio-\nrity.Nbr','Type','Conn-\nected\nTo','rrWhile\ntimer','rbWhile\ntimer', 'fdWhile\ntimer','rcvd-\nInfo-\nWhile\ntimer',\
#                'pro-\nposing','pro-\nposed','agreed', 'Dup-\nlex', 'Speed', 'Root-\nGuard','BPDU\nGuard','Port-\nfast','Port\nvector']
        headers = ['Inter-\nface','Role','Status', 'Cost', 'Cost\ntow-\nards\nroot','Prio-\nrity.Nbr','Type','Conn-\nected\nTo',\
                'Dup-\nlex', 'Speed', 'Root-\nGuard','BPDU\nGuard','Port-\nfast']
        data = []
        for p in br.ports:
            row = []
            row.append(p.port_name)  
            row.append(p.port_role)
            row.append(p.port_state)
            row.append(str(int(p.port_cost,16)))
            if(p.port_role == "Root" or p.port_role == "Alternate"):
                row.append(str(int(p.root_path_cost,16)))
            else:
                row.append(str(0))
            row.append(str(int(p.port_id[0:2],16))+"."+str(int(p.port_id[2:4],16)))
            row.append(p.port_type)
            row.append(p.peer_name)
  #          row.append(p.rrWhile)
  #          row.append(p.rbWhile)
  #          row.append(p.fdWhile)
  #          row.append(p.rcvdInfoWhile)
  #          row.append(p.proposing)
  #          row.append(p.proposed)
  #          row.append(p.agreed)
#            row.append(p.root_priority)
#            row.append(p.root_mac)
            row.append(p.duplex)
            row.append(p.speed)
            row.append(p.rootguard)
            row.append(p.bpduguard)
            row.append(p.portfast)
  #          row.append(p.get_port_priority_vector())
            data.append(row)
        print(tabulate.tabulate(data, headers, tablefmt='simple'))
        print("")

    def print_menu(self,bridges,menu_var):
        if(int(menu_var)==11):

            print("\nThe maximum age timer specifies the maximum expected arrival time of  hello BPDUs.\nIf the maximum age timer expires, the bridge detects that  the link to the root bridge has failed\nand initiates a topology  reconvergence. The maximum age timer should be longer than the  configured hello timer.\nEven when setting Maximum age in this application, will affect what is maximum_age is being transmitted within a BPDU, it will not affect anything else, as maximum age is a legacy\nfeature used by STP.\nIn our application when port is disconnected, reset port method is used to reset root port and rrWhile timer which is equal to forward_delay\n")

            bridge_nr = helpers.get_number("Enter Bridge number 0 - ", len(bridges)-1)
            if(bridge_nr or bridge_nr==0):                          # if value returned -1, then selection was out of range
                max_age = helpers.get_number("Enter Max Age value 1 - ", MAX_AGE_STATIC)
                if(max_age):
                    bridges[bridge_nr].set_max_age(max_age)
                    print("Bridge max age set to: " + str(int(bridges[bridge_nr].max_age[0:2],16)))
                else: print("Incorrect value.")
            else: print("Incorrect selection.")
        elif(int(menu_var)==12):
            bridge_nr = helpers.get_number("Enter Bridge number 0 - ", len(bridges)-1)
            if(bridge_nr or bridge_nr==0):                          # if value returned -1, then selection was out of range
                hello_time = helpers.get_number("Enter Hello Time value 1 - ",MAX_HELLO_TIME_STATIC)
                if(hello_time):                          # if value returned -1, then selection was out of range
                    bridges[bridge_nr].set_hello_time(hello_time)
                    print("Bridge hello time set to: "+str(int(bridges[bridge_nr].hello_time[0:2],16))+"\n")
                else: print("Incorrect value")
            else: print("Incorrect selection.")

        elif(int(menu_var)==13):
            print("""\nThe forward delay timer only applies on the ports, where a switch can't perform RSTP sync process.
If the neighbouring switch can't do proposal/agreement exchange, then port reverts back to standard STP rules.
In this application, if port became live and it did not receive proposal/agreement flags, it will go through STP convergence process:
1. Wait in \"Discarding\" state for forward_delay value seconds
1. Wait in \"Learning\" state for forward_delay value seconds
3. Switch to \"Forwarding\" state\n
(Total 30 seconds to switch port to \"Forwarding\" state if forward delay set to 15 seconds)\n""")
            bridge_nr = helpers.get_number("Enter Bridge number 0 - ", len(bridges)-1)
            if(bridge_nr>=0):
                forward_delay = helpers.get_number("Enter Forward Delay value 1 - ", MAX_FORWARD_DELAY_STATIC)
                if(forward_delay):                          # if value returned -1, then selection was out of range
                    bridges[bridge_nr].set_forward_delay(forward_delay)
                    print("Bridge Forward Delay set to: "+ str(int(bridges[bridge_nr].forward_delay[0:2],16))+"\n")
                else: print("Incorrect value.")
            else: print("Incorrect selection.")
        elif(int(menu_var)==16):
            print("""The root guard ensures that the port on which root guard is enabled is the designated port.
Normally, root bridge ports are all designated ports, unless two or more ports of the root bridge are connected together.
If the bridge receives superior STP Bridge Protocol Data Units (BPDUs) on a root guard-enabled port, root guard moves this 
port to a root-inconsistent STP state. This root-inconsistent state is effectively equal to a listening state.
No traffic is forwarded across this port. In this way, the root guard enforces the position of the root bridge.
More info: https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/10588-74.html""")
            bridge_nr = helpers.get_number("Enter Bridge number 0 - ", len(bridges)-1)
            if(bridge_nr>=0):
                port_nr = helpers.get_number("Enter Port number: 0 - ", PORTS_PER_BRIDGE-1)
                if(port_nr>=0):
                    d_e = helpers.get_number("Select number:\n1. Enable Root Guard on port\n2. Disable root Guard on port\nEnter 1 -",2)
                    if(d_e == 1):
                        bridges[bridge_nr].ports[port_nr].rootguard = True
                        print("Port "+bridges[bridge_nr].ports[port_nr].port_name+" Root Guard disabled. Superior BPDU can arrive on this port")
                    elif(d_e ==2):
                        bridges[bridge_nr].ports[port_nr].rootguard = False
                        print("Port "+bridges[bridge_nr].ports[port_nr].port_name+" Root Guard enabled. If superior BPDU arrives on this port, it will enter \"Err_Disabled\" state.")
                    else: print("Incorrect selection.")


        elif(int(menu_var)==10):
            print("\nBridge with lowest priority in the network will become root.\nValid Bridge priorities are in the range 0 through 61440, in steps of 4096 (IEEE 802.1D-2004 section 14.3)\n")
            bridge_nr = helpers.get_number("Enter Bridge number 0 - ", len(bridges)-1)
            if(bridge_nr>=0):
                bridge_priority = input("Enter Bridge Priority (0 4096 8192 12288 16384 20480 24576 28672 32768 36864 40960 45056 49152 53248 57344 61440): ")
                bridges[bridge_nr].set_bridge_priority(int(bridge_priority))            ## set_bridge_priority module will check if correct value
                print("\nBridge Priority set to: " + str(int(bridges[bridge_nr].bridge_priority,16))+" (priority + VLAN ID 1)\n")
            else: print("Incorrect value.")
        elif(int(menu_var)==14):                         # set port cost per bridge
            print("""\nRSTP will select a best path towards root bridge which has lowest sum of all cost root port costs. It is important to note that \"sum of ROOT PORT\" costs and not
Designated ports. As an example There are 3 bridges connected B1/B2/B3. P0/P1/P5/P6 are port numbers. B1_P0->B2_P1; B2_P5->B3_P6.
Root bridge is B1. If all ports are 1Gb/s, then default cost per port is 20000.
B1 advertises cost of 0 to B2_P1
B2 advertises cost of 20000 to B3_P6
B3 total cost to root bridge is 40000 (Because it's root port B3_P6 20000 is added to what B2 advertised)
Changing port cost of P0 or P5 will not have any effect on the total cost to root path from B3  (because these ports are \"Designated\"
Instead, to change root path cost, change only "ROOT PORT cost": P1 or P6\n""")
            bridge_nr = helpers.get_number("Enter Bridge number 0 - ", len(bridges)-1)
            if(bridge_nr>=0):
                port_nr = helpers.get_number("Enter Port number: 0 - ", PORTS_PER_BRIDGE-1)
                if(port_nr>=0):
                    print("\nSet cost 1-200000000. Recommended cost per speed:\n200000000 - 100kbps\n20000000 - 1Mbps\n2000000 - 10Mbps\n200000 - 100Mbps\n20000 - 1Gbps\n2000 - 10Gbps\n")
                    path_cost = helpers.get_number("Enter Cost: ", 200000000)
                    if(path_cost):
                        bridges[bridge_nr].ports[port_nr].set_port_cost(path_cost)
                    else: print("Incorrect value.")
                else: print("Incorrect selection.")
            else: print("Incorrect selection.")
        elif(int(menu_var)==15):
            print("""\nChanging Port priority never affects the current bridge where the port priority is changed.
Instead, it can affect the bridge which connects to that ports. Lets say we have two bridges connected with two ports to each other:

B1_P1 -> B2_P7
B1_P5 -> B2_P3

B1 is a root bridge and both P1 & P5 ports are having \"Designated\" role and sending BPDUs every hello_timer seconds.
If all settings are default, B2 will set its port P7 as ROOT_PORT, and B2_P3 as ALTERNATE_PORT. This is because
if both P1&P5 have same default priority (128), then the lower port ID is better. So when Superior BPDUs received on B2 ports P7&P3,
B2 must decide which port must become root, and will select port B1_P1, because it's port ID is lower.
If chaning port B1_P5 priority to 100, Bridge B2 topology will change and it will set it's root port as P3 and alternate port as P7.\n""")
            bridge_nr = helpers.get_number("Enter Bridge number 0 - ", len(bridges)-1)
            if(bridge_nr>=0):
                port_nr = helpers.get_number("Enter port number: 0 - ", PORTS_PER_BRIDGE-1)
                if(port_nr>=0):
                    port_priority = helpers.get_number("Enter port priority 0 - ", PORT_PRIORITY_MAX)
                    if(port_priority):
                        bridges[bridge_nr].ports[port_nr].set_port_priority(port_priority)
                    else: print("Incorrect value.")
                else: print("Incorrect selection.")
            esle: print("Incorrect selection.")
        elif(int(menu_var)==16):
            print("unimplemented")
        elif(int(menu_var)==17):
            print("""At the reception of BPDUs, the BPDU guard operation disables the port that has PortFast configured.
The BPDU guard transitions the port into errdisable state
More information regarding RSTP/STP BPDU Guard enchancement: https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/10586-65.html\n""")
            bridge_nr = helpers.get_number("Enter Bridge number 0 - ", len(bridges)-1)
            if(bridge_nr>=0):
                port_nr = helpers.get_number("Enter port number: 0 - ", PORTS_PER_BRIDGE-1)
                if(port_nr>=0):
                    bpduguard = helpers.get_number("Select number:\n1. Enable BPDU Guard\n2. Disable BPDU Guard\nEnter 1 - ",2)
                    if(bpduguard == 1):
                        bridges[bridge_nr].ports[port_nr].bpduguard = True
                        print("BPDU Guard enabled on port "+bridges[bridge_nr].ports[port_nr].port_name+". This will put port into \"Err_diabled\" state when any (superior or not) RSTP BPDU received.")
                    elif(bpduguard == 2):
                        bridges[bridge_nr].ports[port_nr].bpduguard = False
                        print("BPDU Guard disabled on port "+bridges[bridge_nr].ports[port_nr].port_name+". This will NOT put port into \"Err_diabled\" state when any (superior or not) RSTP BPDU received.")

        elif(int(menu_var)==18):
            print("\nChanging speed, will chante RSTP port cost (as per values below). Cost can be changed after manually using option 14.\nBelow are the default recommended port cost per speed as per IEEE 802.1w-2001 specification Table 17-7\n")
            bridge_nr = helpers.get_number("Enter Bridge number 0 - ", len(bridges)-1)
            if(bridge_nr>=0):
                port_nr = helpers.get_number("Enter port number: 0 - ", PORTS_PER_BRIDGE-1)
                if(port_nr>=0):
                    speed = helpers.get_number("\nSelect speed:\n1. 10 Tb/s\t(RSTP cost: 2)\n2. 1 Tb/s\t(RSTP cost: 20\n3. 100 Gb/s\t(RSTP cost: 200)\n4. 10 Gb/s\t(RSTP cost: 2000)\n5. 1 Gb/s\t(RSTP cost: 20000)\n6. 100 Mb/s\t(RSTP cost: 200000)\n7. 10 Mb/s\t(RSTP cost: 2000000)\n\nEnter 1 - ",7)
                    if(speed == 1):
                        bridges[bridge_nr].ports[port_nr].speed = 10000000000  #10Tb/s
                        #bridges[bridge_nr].ports[port_nr].update_speed(10000000000)  #10Tb/s
                        bridges[bridge_nr].ports[port_nr].set_port_cost(2)
                    elif(speed == 2):
                        bridges[bridge_nr].ports[port_nr].speed = 1000000000  #1Tb/s
                        #bridges[bridge_nr].ports[port_nr].update_speed(1000000000)  #1Tb/s
                        bridges[bridge_nr].ports[port_nr].set_port_cost(20)
                    elif(speed == 3):
                        bridges[bridge_nr].ports[port_nr].speed = 100000000  #100Gb/s
                        #bridges[bridge_nr].ports[port_nr].update_speed(100000000)  #100 Gb/s
                        bridges[bridge_nr].ports[port_nr].set_port_cost(200)
                    elif(speed == 4):
                        bridges[bridge_nr].ports[port_nr].speed = 10000000  #10Gb/s
                        #bridges[bridge_nr].ports[port_nr].update_speed(10000000)  #10Gb/s
                        bridges[bridge_nr].ports[port_nr].set_port_cost(2000)
                    elif(speed == 5):
                        bridges[bridge_nr].ports[port_nr].speed = 1000000  #1Gb/s
                        #bridges[bridge_nr].ports[port_nr].update_speed(1000000)  #1Gb/s
                        bridges[bridge_nr].ports[port_nr].set_port_cost(20000)
                    elif(speed == 6):
                        bridges[bridge_nr].ports[port_nr].speed = 100000  #100Mb/s
                        #bridges[bridge_nr].ports[port_nr].update_speed(100000)  #100Mb/s
                        bridges[bridge_nr].ports[port_nr].set_port_cost(200000)
                    elif(speed == 7):
                        bridges[bridge_nr].ports[port_nr].speed = 10000  #10Mb/s
                        #bridges[bridge_nr].ports[port_nr].update_speed(10000)  #10Mb/s
                        bridges[bridge_nr].ports[port_nr].set_port_cost(2000000)
                    else: print("Incorrect seletion: "+str(speed))

        elif(int(menu_var)==19):            # Set link-type: Full-duplex or Half-duplex
            print("Setting port duplex type. As per 802.1d-2004 section 6.5.1 - Link type becomes P2P if Full-duplex is set on a port.\nWhen changing duplex, currently it affects only link type status (set P2P or Shared).")
            bridge_nr = helpers.get_number("Enter Bridge number 0 - ", len(bridges)-1)
            if(bridge_nr>=0):
                port_nr = helpers.get_number("Enter port number: 0 - ", PORTS_PER_BRIDGE-1)
                if(port_nr>=0):
                    edge_set = helpers.get_number("Select number:\n1. Set port as Full-duplex\n2. Set port as Half-duplex\nEnter 1 - ",2)
                    if(edge_set == 1):
                        bridges[bridge_nr].ports[port_nr].duplex = "Full"
                        bridges[bridge_nr].ports[port_nr].port_type = "P2P"
                        print("Port "+bridges[bridge_nr].ports[port_nr].port_name+" set to Full-duplex. This affects if the link is \"P2P\".")
                    elif(edge_set == 2):
                        bridges[bridge_nr].ports[port_nr].duplex = "Half"
                        bridges[bridge_nr].ports[port_nr].port_type = "Shared"
                        print("Port "+bridges[bridge_nr].ports[port_nr].port_name+" set to Half-duplex. This will make RSTP link type as \"Shared\".")
                    else: print("Incorrect selection.")
        elif(int(menu_var)==20):
            print("""In order to allow immediate transition of the port into forwarding state, enable the STP PortFast feature.
PortFast immediately transitions the port into STP forwarding mode upon linkup. The port still participates in STP.
As long as the port participates in STP, some device can assume the root bridge function and affect active STP topology.""")
            bridge_nr = helpers.get_number("Enter Bridge number 0 - ", len(bridges)-1)
            if(bridge_nr>=0):
                port_nr = helpers.get_number("Enter port number: 0 - ", PORTS_PER_BRIDGE-1)
                if(port_nr>=0):
                    portfast = helpers.get_number("Select number:\n1. Enable PortFast on a port\n2. Disable Portfast on a port\nEnter 1 - ",2)
                    if(portfast == 1):
                        bridges[bridge_nr].ports[port_nr].portfast = True
                        print("Portfast enabled on port "+bridges[bridge_nr].ports[port_nr].port_name+". This will switch port into Forwarding immediately on topology changes.")
                    elif(portfast == 2):
                        bridges[bridge_nr].ports[port_nr].portfast = False
                        print("Portfast disabled on port "+bridges[bridge_nr].ports[port_nr].port_name+". This will slow down transition of port to Forwarding state")
                    else: print("Incorrect selection.")
                else: print("Incorrect selection.")
            else: print("Incorrect selection.")

        elif(int(menu_var)==21):
            bridge_nr = helpers.get_number("Enter Bridge number 0 - ", len(bridges)-1)
            if(bridge_nr>=0):
                port_nr = helpers.get_number("Enter port number: 0 - ", PORTS_PER_BRIDGE-1)
                if(port_nr >= 0):
                    d_e = helpers.get_number("Select number:\n1. Enable port\n2. Disable port\nEnter 1 -",2)
                    if(d_e ==1):
                        bridges[bridge_nr].ports[port_nr].portEnabled = True
                        bridges[bridge_nr].ports[port_nr].reset_port_priority_vector()
                        print("Port "+bridges[bridge_nr].ports[port_nr].port_name+" enabled.")
                    elif(d_e == 2):
                        bridges[bridge_nr].ports[port_nr].reset_port_priority_vector()
                        bridges[bridge_nr].ports[port_nr].portEnabled = False
                        bridges[bridge_nr].ports[port_nr].port_state = "Disabled"
                        bridges[bridge_nr].ports[port_nr].port_role = "Disabled"
                        print("Port "+bridges[bridge_nr].ports[port_nr].port_name+" disabled. It will not send or receive BPDUs")
                    else: print("Incorrect selection.")
                else: print("Incorrect selection.")
            else: print("Incorrect selection.")

        elif(int(menu_var)==1):             # Print bridge status
            bridge_nr = helpers.get_number("Enter Bridge number 0 - ", len(bridges)-1)
            if(bridge_nr or bridge_nr==0):                          # if value returned -1, then selection was out of range
                self.print_bridge_status(bridges[bridge_nr])
            else: print("Incorrect selection.")
        elif(int(menu_var)==30):
            print("Connect Brige Port to a network card")
            bridge_nr = helpers.get_number("Enter Bridge number 0 - ", len(bridges)-1)
            if(bridge_nr>=0):
                port_nr = helpers.get_number("Enter port number: 0 - ", PORTS_PER_BRIDGE-1)
                if(port_nr>=0):
                    helpers.print_physical_interfaces() 
                    card_name = input("Enter network card name from the list above:")
                    if(card_name in helpers.get_physical_interfaces()):
                        print("Connecting port "+bridges[bridge_nr].ports[port_nr].port_name+" to "+card_name)
                        bridges[bridge_nr].connect_to_network_card(port_nr,card_name)
                    else: print("Incorrect selection.")
                else: print("Incorrect selection.")
            else: print("Incorrect selection.")

        elif(int(menu_var)==35):
            print("Connect Bridge port to another Bridge port")
            bridge_nr = helpers.get_number("Enter Bridge number 0 - ", len(bridges)-1)
            if(bridge_nr>=0):
                port_nr = helpers.get_number("Enter port number: 0 - ", PORTS_PER_BRIDGE-1)
                if(port_nr>=0):
                    #bridges[bridge_nr].connect_to_other_bridge_port(bridges,port_nr)
#                    print("Brnr:"+str((bridge_nr))
#                    print("Prnr:"+str(port_nr))
                    all_ports= []                       # all ports apart from current bridge. 3x4 = 12 ports
                    all_ports_names = []                # all ports names apart from current bridge. 3x4 = 12 port names
                    print("Select from port list below (rstp-4-1 means Port 1 on Bridge 4)")
                    c=1
                    print("Connecting bridge"+str(bridge_nr))
                    print("There are in total bridges: "+str(len(bridges)))
                    for i in bridges:
                        for p in i.ports:                       # Loop all ports on a bridge
                            if(not (i.bridge_nr == bridge_nr and p.port_nr == port_nr)):     # If it is not the same port&bridge which connecting
                                # Output all ports. c is a counter which will be used further to select a port
                                print(str(c)+". Bridge"+str(i.bridge_nr)+" port"+str(p.port_nr)+" (int:"+p.port_name+") connected to: "+p.peer_name)
                                c=c+1
                                all_ports.append(p)
                    selected_port = int(input("Enter number of selection 1-"+str(c-1)+": "))            # c-1 is required because after incrementing it in the loop, loop ended.
                    if(selected_port >=1 or selected_port < c):
                        print("Selected to connect to: "+str(selected_port))
                        print("Connecting to: "+all_ports[selected_port-1].port_name)
                        bridges[bridge_nr].connect_port_to_port(port_nr,all_ports[selected_port-1])
                    else:
                        print("Incorrect selection: exit")
                        exit()
                else: print("Incorrect selection.")
            else: print("Incorrect selection.")




        elif(int(menu_var)==40):
            print("Disconnect port:")
            bridge_nr = helpers.get_number("Enter Bridge number 0 - ", len(bridges)-1)
            if(bridge_nr>=0):
                port_nr = helpers.get_number("Enter port number: 0 - ", PORTS_PER_BRIDGE-1)
                if(port_nr>=0):
                    bridges[bridge_nr].ports[port_nr].disconnect_port()
                else: print("Incorrect selection.")
            else: print("Incorrect selection.")
        elif(int(menu_var)==3):
            bridge_nr = helpers.get_number("Enter Bridge number 0 - ", len(bridges)-1)
            if(bridge_nr>=0):
                port_nr = helpers.get_number("Enter port number: 0 - ", PORTS_PER_BRIDGE-1)
                if(port_nr>=0):
                    bridges[bridge_nr].ports[port_nr].this_logger.print_logs()
                else: print("Incorrect selection.")
            else: print("Incorrect selection.")
        elif(int(menu_var)==2):
            bridge_nr = helpers.get_number("Enter Bridge number 0 - ", len(bridges)-1)
            if(bridge_nr or bridge_nr==0):                          # if value returned -1, then selection was out of range
                bridges[bridge_nr].this_logger.print_logs()
            else: print("Incorrect selection.")
        elif(int(menu_var)==4):
            self.print_all_bridge_connections(bridges)
        elif(int(menu_var)==45):
            helpers.generate_graphviz(bridges,False)            # if True, then generate just rstp_graph.png, do not output graph in text to stdout
        elif(int(menu_var)==5):
            helpers.show_traffic_stats()
        elif(int(menu_var)==50):
            helpers.add_bridge(bridges,bridge)
        elif(int(menu_var)==55):
       #     bridge_nr = helpers.get_number("Enter Bridge number 0 - ", len(bridges)-1)
       #     if(bridge_nr or bridge_nr==0):                          # if value returned -1, then selection was out of range
       #         helpers.terminate_bridge(bridges,bridge_nr)
        #    else: print("Incorrect selection.")
            helpers.pop_bridge(bridges)
        elif(int(menu_var)==60):
            maxx = len(bridges[0].ports)
            maxx = int(maxx/2)
            maxx = helpers.get_number("How many ports to connect on each bridge 1 - ", maxx)
            if(maxx):
                helpers.generate_random_topology(bridges,maxx)
            else: print("Incorrect selection.")
        elif(int(menu_var)==65):
            print("""Select topology from the list:
1. Toploggy - description A
2. Topology - description A
3. Topology - https://www.youtube.com/watch?v=N_gBudULCu0
4. Topology - https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/24062-146.html
5. Topology
6. Topology
7. Topology
8. Topology
9. Topology 
10.Topology
11.Topology """)
            top_selection = helpers.get_number("Enter Topology selection number 0 - ", 11)
            if(top_selection==1):
                        helpers.generate_example_topology(bridges,bridge,1)
            if(top_selection==2):
                        helpers.generate_example_topology(bridges,bridge,2)
            if(top_selection==3):
                        helpers.generate_example_topology(bridges,bridge,3)
            if(top_selection==4):
                        helpers.generate_example_topology(bridges,bridge,4)
            if(top_selection==5):
                        helpers.generate_example_topology(bridges,bridge,5)
            if(top_selection==6):
                        helpers.generate_example_topology(bridges,bridge,6)
            if(top_selection==7):
                        helpers.generate_example_topology(bridges,bridge,7)
            if(top_selection==8):
                        helpers.generate_example_topology(bridges,bridge,8)
            if(top_selection==9):
                        helpers.generate_example_topology(bridges,bridge,9)
            if(top_selection==10):
                        helpers.generate_example_topology(bridges,bridge,10)
            if(top_selection==11):
                        helpers.generate_example_topology(bridges,bridge,11)
        elif(int(menu_var)==99):
            helpers.cleanup_and_exit(bridges)
        elif(int(menu_var)==0):
            self.show_menu(bridges)
        else:
            print("Unknown menu selectoin.")

    def show_menu(self,bridges):
        headers = ['RSTP Get setting', 'RSTP Set setting', 'Other settings']
        col1= []
        col2= []
        col3= []
        data =[]
        col1.append("0.  Show this menu")
        col1.append("99. Cleanup and Exit")
        col1.append("1.  Print Bridge Status")
        col1.append("2.  Print Bridge Logs")
        col1.append("3.  Print Port Logs")
        col1.append("4.  Print all connections")
        col1.append("5.  Print traffic stats")
        col1.append("")
        col1.append("")
        col1.append("")
        col1.append("")
        col1.append("")
        col1.append("")
        col1.append("")
        col2.append("10. Set Bridge Priority")
        col2.append("11. Set Max Age")
        col2.append("12. Set Hello Time")
        col2.append("13. Set Forward Delay")
        col2.append("14. Set Cost on port")
        col2.append("15. Set port Priority")
#        col2.append("16. Set port type (unimplemented)")
        col2.append("16. Set Root Guard on port")
        col2.append("17. BPDU Guard")
        col2.append("18. Set link speed")
        col2.append("19. Set link duplex type")
        col2.append("20. Set Portfast")
        col2.append("21. Disable/Enable port")

        col3.append("30. Connect Bridge Port to physical network card")
        col3.append("35. Connect Bridge Port to another this app Bridge port")
        col3.append("40. Disconnect Port")
        col3.append("45. Generate Graphviz topology graph")
        col3.append("50. Add bridge")
        col3.append("55. Terminate last bridge")
        col3.append("60. Generate random topology")
        col3.append("65. Preload example topology")
        col3.append("")
        col3.append("")
        col3.append("")
        col3.append("")

#        print(tabulate.tabulate(data,headers,tablefmt='simple'))
        print(tabulate.tabulate(list(zip(col1,col2,col3)),headers,tablefmt='simple'))
