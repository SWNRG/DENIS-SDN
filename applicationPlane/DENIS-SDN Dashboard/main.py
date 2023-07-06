"""
DENIS-SDN Dashboard
Is the GUI of DENIS-SDN, an SDN solution for Ultradense IoT Network environments consisting
of a modular SDN controller and an OpenFlow-like data-plane protocol.

Author: Tryfon Theodorou
Website: www.theodorou.edu.gr
GitHub: tryfonthe

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import socket
import json
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk
import time
import sys


def process_json_message(json_data):
    try:
        # Parse the JSON message
        message = json.loads(json_data)

        # Access the nodes and links in the JSON message
        nodes = message['nodes']
        links = message['links']

        # Add nodes to the graph
        for node in nodes:
            if 'id' in node:
                node_id = node['id']
            else:
                print("JSON message contains node with no ID")
                node_id = 0
            if 'desc' in node:
                node_desc = node['desc']
            else:
                node_desc = node_id
            if 'slice' in node:
                node_slice = node['slice']
            else:
                node_slice = 1
            if 'class' in node:
                node_class = node['class']
            else:
                node_class = "Node"
            G.add_node(node_id, desc=node_desc, slice=node_slice, n_class=node_class)

        # Add links to the graph
        for link in links:
            source = link['source']
            target = link['target']
            G.add_edge(source, target)

        print('JSON message processed successfully.')

    except json.JSONDecodeError as e:
        print('Error decoding JSON:', e)

def draw_graph():
    global pos
    global node_colors
    # Clear the previous graph
    plt.clf()

    # Draw the graph
    #pos = nx.spring_layout(G)
    #nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, edge_color='gray')
    nx.draw_networkx_nodes(G, pos, node_color=[node_colors[node] for node in G.nodes], node_size=500, alpha=0.7)
    #nx.draw_networkx_edge_labels(G, pos)

    #pos = nx.spring_layout(G)
    #nx.draw_networkx_nodes(G, pos, node_color=[node_colors[node] for node in G.nodes], node_size=450, alpha=0.7)
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos)
    plt.axis("off")

    # Show the graph
    #plt.show()
    canvas.draw()

# Drag and drop nodes
def on_press(event):
    global drag_node
    if event.inaxes is None:
        return
    for node in pos:
        node_x, node_y = pos[node]
        if abs(node_x - event.xdata) < 0.05 and abs(node_y - event.ydata) < 0.05:
            drag_node = node
            break

def on_release(event):
    global drag_node
    drag_node = None

def on_motion(event):
    global drag_node
#    print("working On_motion drag_node=",drag_node)
    if drag_node is not None and event.inaxes is not None:
        pos[drag_node] = (event.xdata, event.ydata)

        draw_graph()

def receive_json_messages():
    global pos
    global neighbors
    global node_colors
    # Define the host and port
    host = 'localhost'
    port = 8993

    # Create a socket connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(1)

    print(f"Listening for JSON messages on port {port}...")

    # Accept incoming connections
    conn, addr = sock.accept()
    print('Connected:', addr)

    #while True:
    while not stop_flag.is_set():
        # Receive data from the client
        data = conn.recv(5024)

        if not data:
            time.sleep(1)  # Wait for 1 second
        else:
            print("Running JSON Read...")
            # Decode the received data
            json_data = data.decode('utf-8')

            # Clear Exiting Graph
            G.clear()

            # Process the JSON message
            process_json_message(json_data)

            pos = nx.spring_layout(G)  # Set positions for Graph nodes

            show_slice_configurator()

            neighbors.clear()
            neighbors = calculate_neighbors_list()
            show_desnsity_classifier(neighbors)

            node_colors.clear()
            node_colors = set_node_colors(neighbors)

            # Update the graph visualization
            draw_graph()

    # Close the connection
    conn.close()
    print("Closing Communication thread with DENIS-SDN Controller...")

# Create the list of colores for the Graph nodes
def set_node_colors(neighbors):
    node_colors = {}

    for node in G:
        for i, row in enumerate(neighbors):
            if node in row:
                node_colors[node] = neighbors[i][2]
                break

    return node_colors

# ===================================================================
# MAIN program
# ===================================================================

MAXnodes=36

# Create the main window
window = tk.Tk()
window.iconbitmap('NetIco.ico')
window.title("DENIS-SDN Dashboard")
window.geometry("1220x670")

# #####################################################################################################
#                                           Slice Configurator                                        #
# #####################################################################################################
# Display the Slice Configurator list
def show_slice_configurator():
    slices = ["Slice {}".format(i) for i in range(1, 17)]

    i = 1
    for node in G.nodes():
        label = tk.Label(listbox_frame, text="Node {}".format(node), font=('Arial', 12), relief=tk.SUNKEN)
        label.grid(row=i, column=0, sticky="we")
        density_list_labels.append(label)

        combobox = ttk.Combobox(listbox_frame, values=slices, state="readonly", font=('Arial', 12), width=10)
        combobox.grid(row=i, column=1, padx=10, sticky="w")
        combobox.set(str("Slice "+str(G.nodes[node]['slice'])))
        combobox.bind("<<ComboboxSelected>>", on_combobox_change)
        density_list_comboboxes.append(combobox)
        i = i+1
        # print(G.nodes[node_id]['desc'], G.nodes[node_id]['slice'], G.nodes[node_id]['n_class'])

# Change the slice of a node using the combobox
def on_combobox_change(event):
    selected_value = event.widget.get()
    combobox_index = density_list_comboboxes.index(event.widget)
    print(f"Combobox #{combobox_index + 1} - Selected value: {selected_value}")

    n = density_list_labels[combobox_index].cget('text') # get node from nodelist
    node_id = n[5:] # remove the word Node
    slice_no = selected_value[6:]  # remove the word Slice
    G.nodes[node_id]['slice'] = int(slice_no)
    print(density_list_labels[combobox_index].cget('text')," ",node_id)

heading1 = tk.Label(window, text="Slice Configurator", font=('Arial',14, 'bold'), background="Light Gray", relief=tk.RAISED, borderwidth=3)
heading1.grid(row=0, column=0, padx=10, sticky="nwe")

# Create the frame for the Density List
density_list_frame = tk.Frame(window, highlightthickness=1, highlightbackground="black")
density_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nw")

# Create the canvas for the Density List
listbox_canvas = tk.Canvas(density_list_frame, height=470, width=245)
listbox_canvas.pack(side="left", fill="y")

# Create the scrollbar for the Density List
scrollbar = tk.Scrollbar(density_list_frame, orient="vertical", command=listbox_canvas.yview)
scrollbar.pack(side="right", fill="y")

# Configure the canvas scrolling
listbox_canvas.configure(yscrollcommand=scrollbar.set)
listbox_canvas.bind("<Configure>", lambda e: listbox_canvas.configure(scrollregion=listbox_canvas.bbox("all")))

# Create the frame inside the canvas
listbox_frame = tk.Frame(listbox_canvas)

# Add the listbox frame to the canvas
listbox_canvas.create_window((0, 0), window=listbox_frame, anchor="nw")

# Create the labels and combo boxes for the Density List
density_list_labels = []
density_list_comboboxes = []

title = tk.Label(listbox_frame, text="Network Nodes", font=('Arial',12), background="Light Gray", relief=tk.RAISED, borderwidth=3)
title.grid(row=0, column=0, sticky="w")
title = tk.Label(listbox_frame, text="Network Slice", font=('Arial',12), background="Light Gray", relief=tk.RAISED, borderwidth=3)
title.grid(row=0, column=1, padx=10, sticky="we")

# #####################################################################################################
#                                  Real-time Slice Manager                                            #
# #####################################################################################################
# Send SLice COnfiguration Data to DENIS-SDN Controller
def send_slice_configuration():
    # Convert the graph to JSON
    graph_data = json_graph.node_link_data(G)
    json_data = json.dumps(graph_data, indent=4)

    print("V1=",json_data)

    # Parse the existing JSON string
    data = json.loads(json_data)

    # Add a new key-value pair
    data['sliceType'] = str(var.get())

    # Convert the updated data back to a JSON string
    json_data = json.dumps(data, indent=4)

    print("V2=",json_data)

    # Define the target host and port
    host = 'localhost'  # Change to the appropriate IP address or hostname
    port = 8993

    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server
        sock.connect((host, port))

        # Send the JSON message
        sock.sendall(json_data.encode())

        # Print a success message
        print("JSON message sent successfully!")

    except ConnectionRefusedError:
        print("Connection refused. Make sure the server is running and the port is correct.")

    finally:
        # Close the socket
        sock.close()

heading3 = tk.Label(window, text="Real-time Slice Manager", font=('Arial', 14, 'bold'), background="Light Gray", relief=tk.RAISED, borderwidth=3)
heading3.grid(row=2, column=0, padx=10, sticky="nwe")

buttons_frame = tk.Frame(window)
buttons_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nw")

# Create the radio buttons
var = tk.StringVar()
var.set("Logically-Sliced")  # Set the initial selection
radio1 = tk.Radiobutton(buttons_frame, text="Logically-Sliced", variable=var, value="Logically-Sliced", font=('Arial',12))
radio2 = tk.Radiobutton(buttons_frame, text="Physically-Sliced", variable=var, value="Physically-Sliced", font=('Arial',12))
radio1.pack(anchor="w")
radio2.pack(anchor="w")

slicer_button = tk.Button(buttons_frame, text="Update Network Slices",font=('Arial',14), command=send_slice_configuration)
slicer_button.pack(anchor="center")  #side="left"

# #####################################################################################################
#                                 Network Density Visualizer                                          #
# #####################################################################################################
heading2 = tk.Label(window, text="Network Density Visualizer", font=('Arial', 14, 'bold'), background="Light Gray", relief=tk.RAISED, borderwidth=3)
heading2.grid(row=0, column=1, padx=10, sticky="nwe")

# Create the network graph
network_graph_frame = tk.Frame(window)
network_graph_frame.grid(row=1, column=1, padx=10, pady=10)

# Create the network graph using networkx and matplotlib
G = nx.Graph()

neighbors = []
node_colors = {}

# Enable drag and drop
drag_node = None

# Create the canvas for the network graph
figure = plt.gcf()
canvas = FigureCanvasTkAgg(figure, master=network_graph_frame)

figure.canvas.mpl_connect('button_press_event', on_press)
figure.canvas.mpl_connect('button_release_event', on_release)
figure.canvas.mpl_connect('motion_notify_event', on_motion)
#canvas.draw()
canvas.get_tk_widget().pack()

# #####################################################################################################
#                                 Connectivity Detector CODET                                         #
# #####################################################################################################
from CODET import run_CODET

# CODET thread
def execute_CODET():
    global node_colors
    print("Starting CODET for every ",codet_combobox.get()," min")

    while not stop_flag.is_set():

        # Sleep
        print("CODET waiting for",codet_combobox.get()," min")
        time.sleep(int(codet_combobox.get())*60)

        # Call CODET Algorithm
        print("Running CODET...")
        DN = run_CODET(G,"00.00")

        # Change the color of the disconnected nodes
        node_colors.clear()
        node_colors = set_node_colors(neighbors)
        for node in DN:
            node_colors[node] = 'gray'

        # Update wrarning message
        #codet_message['text'] = "Warning!!!\n Node(s) ",DN," are disconnected"
        codet_message.config(text=("Warning!!!\n Node(s) "+str(DN)+" are disconnected"))
        # Update the graph visualization
        draw_graph()

    print("Stoping CODET...")

# Button update refresh time
def update_refresh_time():
    global CODET_refresh_time;
    CODET_refresh_time = int(codet_combobox.get())

heading4 = tk.Label(window, text="Connectivity Detector - (CODET)", font=('Arial', 14, 'bold'), background="Light Gray", relief=tk.RAISED, borderwidth=3)
heading4.grid(row=2, column=1, padx=10, sticky="nwe")

codet_frame = tk.Frame(window)
codet_frame.grid(row=3, column=1, padx=10, pady=10, sticky="nwe")

codet_message = tk.Label(codet_frame, text="", font=('Arial',12), fg="Red", background="Light Yellow", relief=tk.SUNKEN, borderwidth=3, wraplength=250)
codet_message.grid(row=0, column=0, sticky="nwe", columnspan=5)

codet_Label = tk.Label(codet_frame, text="                                   CODET Refresh time (min): ", font=('Arial',12))
codet_Label.grid(row=1, column=0, padx=10, pady=5, sticky="nwe")

min = [1,2,3,4,5,6,7,8,10,11,12,13,14,15,16,17,18,19,20,30,40,50,60]
codet_combobox = ttk.Combobox(codet_frame, values=min, state="readonly", font=('Arial', 12), width=5)
codet_combobox.grid(row=1, column=1, padx=10, pady=5, sticky="nwe")
codet_combobox.set('10')

CODET_refresh_time = 10
codet_button = tk.Button(codet_frame, text="Update Refresh time",padx=10,font=('Arial',12), width=15, command=update_refresh_time)
codet_button.grid(row=1, column=3, padx=10, pady=2, sticky="nwe")

# #####################################################################################################
#                                     Node Density Classifier                                         #
# #####################################################################################################
# Create the Neighbor list for the Node Density Classifier
def calculate_neighbors_list():
    neighbors = []

    # Find the number of edges for each node
    node_degrees = dict(G.degree())

    # Add the node degrees
    for node, degree in node_degrees.items():
        neighbors.append((node,degree,''))

    # Sort nodes from node with most neighbors
    neighbors.sort(key=lambda x: -x[1])

    # Split the nodes in four parts
    red_n = neighbors[int(G.number_of_nodes()*0.25)][1]
    orange_n = neighbors[int(G.number_of_nodes()*0.50)][1]
    yellow_n = neighbors[int(G.number_of_nodes()*0.75)][1]

    # Color nodes based on number of neighbors
    for i in range(len(neighbors)):
        element = list(neighbors[i])
        if element[1] <= yellow_n:
            element[2] = 'green'
        elif element[1] <= orange_n:
            element[2] = 'yellow'
        elif element[1] <= red_n:
            element[2] = 'orange'
        else:
            element[2] = 'red'
        neighbors[i] = tuple(element)

    return neighbors

# Display the density classifier list
def show_desnsity_classifier(neighbors):
    for i in range(1, len(neighbors)+1):
        label1 = tk.Label(listbox_classifier_frame, text="Node {}".format(neighbors[i - 1][0]), font=('Arial', 12),
                          relief=tk.SUNKEN, width=10, background=neighbors[i - 1][2])
        label1.grid(row=i, column=0, sticky="we")
        density_classifier_list_labels1.append(label1)

        label2 = tk.Label(listbox_classifier_frame, text="{}".format(neighbors[i - 1][1]), font=('Arial', 12),
                          relief=tk.SUNKEN, width=8)
        label2.grid(row=i, column=1, sticky="we", padx=10)
        density_classifier_list_labels2.append(label2)

heading5 = tk.Label(window, text="Node Density Classifier", font=('Arial', 14, 'bold'), background="Light Gray", relief=tk.RAISED, borderwidth=3)
heading5.grid(row=0, column=3, padx=10, sticky="nwe")

density_classifier_list_labels1 = []
density_classifier_list_labels2 = []

# Create the frame for the Density List
density_classifier_frame = tk.Frame(window, highlightthickness=1, highlightbackground="black")
density_classifier_frame.grid(row=1, column=3, padx=10, pady=10, sticky="nw")

# Create the canvas for the Density List
listbox_classifier_canvas = tk.Canvas(density_classifier_frame, height=470, width=230)
listbox_classifier_canvas.pack(side="left", fill="y")

# Create the scrollbar for the Density List
scrollbar_classifier = tk.Scrollbar(density_classifier_frame, orient="vertical", command=listbox_classifier_canvas.yview)
scrollbar_classifier.pack(side="right", fill="y")

# Configure the canvas scrolling
listbox_classifier_canvas.configure(yscrollcommand=scrollbar_classifier.set)
listbox_classifier_canvas.bind("<Configure>", lambda e: listbox_classifier_canvas.configure(scrollregion=listbox_classifier_canvas.bbox("all")))

# Create the frame inside the canvas
listbox_classifier_frame = tk.Frame(listbox_classifier_canvas)

# Add the listbox frame to the canvas
listbox_classifier_canvas.create_window((0, 0), window=listbox_classifier_frame, anchor="nw")

# Create the labels and combo boxes for the Density List
title = tk.Label(listbox_classifier_frame, text="Network Nodes", font=('Arial',12), background="Light Gray", relief=tk.RAISED, borderwidth=3)
title.grid(row=0, column=0, sticky="we")
title = tk.Label(listbox_classifier_frame, text="# Neighbors", font=('Arial',12), background="Light Gray", relief=tk.RAISED, borderwidth=3)
title.grid(row=0, column=1, padx=10, sticky="we")
#for i in range(1, len(neighbors)):
#    label1 = tk.Label(listbox_classifier_frame, text="Node {}".format(neighbors[i-1][0]), font=('Arial',12), relief=tk.SUNKEN, width=10, background=neighbors[i-1][2])
#    label1.grid(row=i, column=0, sticky="we")
#    density_classifier_list_labels1.append(label1)

#    label2 = tk.Label(listbox_classifier_frame, text="{}".format(neighbors[i-1][1]), font=('Arial',12), relief=tk.SUNKEN, width=8)
#    label2.grid(row=i, column=1, sticky="we", padx=10)
#    density_classifier_list_labels2.append(label2)

# GUI Control
# #######################################################
def close_application():
    stop_flag.set()  # Set the flag to signal the thread to stop
    window.destroy()
    sys.exit()

def start_Dashboard():
    thread.start()
    CODET_thread.start()

def stop_Dashboard():
    stop_flag.set()  # Set the flag to signal the thread to stop

heading6 = tk.Label(window, text="DENIS-SDN Control", font=('Arial', 14, 'bold'), background="Light Gray", relief=tk.RAISED, borderwidth=3)
heading6.grid(row=2, column=3, padx=10, sticky="nwe")

buttons2_frame = tk.Frame(window)
buttons2_frame.grid(row=3, column=3, padx=10, pady=10, sticky="nw")

# Create the buttons
start_button = tk.Button(buttons2_frame, text="Start", font=('Arial',14), width=5, command=start_Dashboard)
start_button.pack(side="left")

stop_button = tk.Button(buttons2_frame, text="Stop",padx=10,font=('Arial',14), width=5, command=stop_Dashboard)
stop_button.pack(side="left", padx=10)

close_button = tk.Button(buttons2_frame, text="Close",padx=10,font=('Arial',14), width=5, command=close_application)
close_button.pack(side="right")

# Run the receive_json_messages function in a separate thread
# to avoid blocking the tkinter main loop
import threading
# Global flag to indicate whether the thread should continue running or stop
stop_flag = threading.Event()

thread = threading.Thread(target=receive_json_messages)

# CODET Thread
CODET_thread = threading.Thread(target=execute_CODET)


# Start the tkinter main loop
window.mainloop()
