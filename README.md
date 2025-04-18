PROGRAM EXECUTION
Program to be executed within Ubuntu (22.04 current version) operating system. 
It will be provided as a compressed folder with all the python code. It will have 
an executable file install_prerequisites.py, which will install additional library 
requirements to start an application. The application itself will be started by 
executing file rstp_2023.py. Arguments can be provided to start an application 
with number of virtual rstp bridges and how many port each of that bridge must 
have: ./rstp_2023.py -b 15 -p 8. This command would start an application with 
initialized 15 bridges, each having 15 ports. Additionally, application will 
create one virtual network card rstp_hub_0. This network card later can be used for 
connecting multiple bridges to it to simulate a hub connectivity. Within an 
application, each virtual port will be called rstp_x_y; x stands for bridge 
number and y for port number. As example rstp_5_7 means bridge 5 and port 7. 
Port and bridge numbers are necessary to know as when using an application, it 
will prompt to input a bridge or a port number. It is necessary to exit 
application using the code 99, otherwise these multiple network cards will stay 
within OS unused.

When started, it will display a CLI menu, when typed in a selection number, it 
will prompt a short description of what the next steps are going to do. Program 
will be waiting for an input from the user to select which bridge or port information 
to be processed or displayed. If wrong selection is done, type in any letter and 
it will bring back to the menu selection. Program will allow to modify all the RSTP 
settings (timers, priorities, etc), connect any rstp virtual bridge to any other 
rstp virtual bridge port or connect to actual existing network card. Depending on 
the user environment, that network card can be connected to physical switch or some 
other any network simulator. Because of that, custom RSTP topologies can be created, 
such as number of rstp_2023 bridges interconnected between each other including one 
two connectivities to external physical network cards.

Application further has multiple pre-programmed topologies which can be loaded, 
including an option to generate a random topology, which will ask used how many 
randomly ports to interconnect. As example if each bridge has 8 ports, application 
will prompt to enter number 1-4, if number 4 is selected, all ports will be connected 
(or sometimes up to 90%, because of the algorithm). Application has an option to export 
current topology as a graph code or image. The image is saved under application 
current folder named rstp_graph.png. The graph code is presented as standard graphviz 
library code and it can be copied and pasted to any website which supports graphviz 
graph presentation. In this project it was used: http://magjac.com/graphviz-visual-editor/. 
If modified any of the bridge parameters and required to refresh the graph, option 45 
must be selected again, which would refresh the image (can be opened already).

Each graph displays a bridge with its number, its mac address and priority represented in 
hex, a total cost towards root bridge, priority of each port, cost of each port, port 
number and what is the role of the port. The active spanning tree non-designated links are 
shown in bold, and alternate or backup links are dashed. Port role names are shortened: Des 
(designated), Alt (alternate), Bac (backup), Roo (root).
