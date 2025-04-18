# RSTP 2023 - Rapid Spanning Tree Protocol Simulator

## 📦 Program Execution

This program is designed to run on **Ubuntu 22.04**. It is distributed as a compressed folder containing all necessary Python files.

### 🔧 Setup

To install required dependencies, run:

```bash
python3 install_prerequisites.py
```

### 🚀 Launch the Application

Start the application using:

```bash
./rstp_2023.py -b 15 -p 8
```

This initializes:

- **15 virtual bridges**
- Each with **8 ports**
- A virtual network card named `rstp_hub_0` (used to simulate hub connectivity between bridges)

## 🔌 Virtual Ports

Each virtual port is named in the format:

```
rstp_<bridge_number>_<port_number>
```

For example: `rstp_5_7` refers to bridge 5, port 7.

> ⚠️ **Note:** Always exit the application by entering code `99` to ensure cleanup of created virtual network cards. Otherwise, unused interfaces will remain in the system.

---

## 🧭 CLI Menu Interface

Upon startup, a **CLI menu** is displayed. Each option shows a short description of the action to be performed. Input prompts will request bridge and port numbers as needed.

- Invalid selections can be dismissed by typing any letter to return to the main menu.
- The user can:
  - Modify RSTP settings (timers, priorities, etc.)
  - Connect any virtual bridge to:
    - Another bridge
    - An actual network card (e.g., to connect to a physical switch or network simulator)

This enables the creation of custom **RSTP topologies**.

---

## 🌐 Topology Options

Features include:

- **Pre-programmed topologies**
- Option to **generate a random topology**

Example: If each bridge has 8 ports, the user will be asked to select a number (1–4) to determine how many random connections are made. Selecting 4 attempts to connect all (or ~90%) of the ports using a randomized algorithm.

---

## 📈 Topology Visualization

The application allows exporting the topology as:

- A **Graphviz DOT code block**
- A **PNG image** saved as `rstp_graph.png` in the current directory

Graphviz code can be viewed using online tools such as:

- [http://magjac.com/graphviz-visual-editor/](http://magjac.com/graphviz-visual-editor/)

> To refresh the graph after modifying topology or bridge parameters, select option `45`.

---

## 📊 Graph Details

Each node (bridge) in the graph displays:

- Bridge number
- MAC address and priority (in hex)
- Total cost toward the root bridge

Each port shows:

- Port number
- Port priority
- Port cost
- Port role

### 🔄 Port Roles (Abbreviated):

- `Des` – Designated
- `Alt` – Alternate
- `Bac` – Backup
- `Roo` – Root

**Bold lines** represent active spanning tree links.  
**Dashed lines** represent alternate or backup links.

---

## 📌 Notes

- Ensure you're running the application with appropriate privileges (some virtual networking may require `sudo`).
- Use code `99` to exit cleanly and prevent lingering virtual interfaces.
