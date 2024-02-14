import networkx as nx
# import itertools
import matplotlib.pyplot as plt
import random
from flask import Flask, render_template, request

app = Flask(__name__)

class Resource:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity
        self.remaining_capacity = capacity

@app.route('/')
def index():
    return render_template('index.html')

def rabin_karp(text, pattern):
    # Rabin-Karp string matching algorithm
    n = len(text)
    m = len(pattern)
    pattern_hash = hash(pattern)
    for i in range(n - m + 1):
        if hash(text[i:i + m]) == pattern_hash:
            if text[i:i + m] == pattern:
                return True
    return False

def categorize_incidents(incident_reports):
    categorized_incidents = {
        "Fire": [],
        "Medical": [],
        "Other": []
    }
    
    for incident in incident_reports:
        description = incident["description"].lower()
        if rabin_karp(description, "fire"):
            categorized_incidents["Fire"].append(incident)
        elif rabin_karp(description, "medical") or rabin_karp(description, "ambulance"):
            categorized_incidents["Medical"].append(incident)
        else:
            categorized_incidents["Other"].append(incident)
    
    return categorized_incidents

def knapsack_allocation(resources, categorized_incidents):
    allocated_resources = {}
    
    for incident_type, incident_list in categorized_incidents.items():
        for categorized_incident in incident_list:
            incident_resources = {resource.name: 0 for resource in resources}
            incident_severity = get_incident_severity(categorized_incident)
            
            for resource in resources:
                if incident_severity == "High":
                    if resource.name == "Fire Truck":
                        allocated = min(3, resource.remaining_capacity)
                    elif resource.name == "Ambulance":
                        allocated = min(2, resource.remaining_capacity)
                    elif resource.name == "Police Car":
                        allocated = min(1, resource.remaining_capacity)
                elif incident_severity == "Medium":
                    if resource.name == "Ambulance":
                        allocated = min(3, resource.remaining_capacity)
                    elif resource.name == "Police Car":
                        allocated = min(2, resource.remaining_capacity)
                    elif resource.name == "Fire Truck":
                        allocated = min(0, resource.remaining_capacity)
                else:
                    if resource.name == "Police Car":
                        allocated = min(2, resource.remaining_capacity)
                    elif resource.name == "Ambulance":
                        allocated = min(1, resource.remaining_capacity)
                    elif resource.name == "Fire Truck":
                        allocated = min(0, resource.remaining_capacity)
                    
                incident_resources[resource.name] += allocated
                resource.remaining_capacity -= allocated
            
            allocated_resources.setdefault(incident_type, []).append(incident_resources)
    
    return allocated_resources


def get_incident_severity(categorized_incident):
    # Simulated function to determine incident severity based on incident details
    description = categorized_incident["description"].lower()
    if "fire" in description:
        return "High"
    elif "medical" in description or "ambulance" in description:
        return "Medium"
    else:
        return "Low"  # Default to low severity if not explicitly identified

def visualize_graph_and_shortest_distances(city_graph, shortest_distances, unit):
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(city_graph)
    nx.draw(city_graph, pos, with_labels=True, node_size=500, node_color='skyblue', font_weight='bold')

    labels = nx.get_edge_attributes(city_graph, 'weight')
    nx.draw_networkx_edge_labels(city_graph, pos, edge_labels=labels, font_color='black')

    for incident, shortest_path in shortest_distances[unit].items():
        if shortest_path != "No path":
            path_edges = [(shortest_path[i], shortest_path[i + 1]) for i in range(len(shortest_path) - 1)]
            edge_labels = {(u, v): d['weight'] for u, v, d in city_graph.edges(data=True)}
            nx.draw_networkx_edges(city_graph, pos, edgelist=path_edges, edge_color='red', width=2)
            nx.draw_networkx_edge_labels(city_graph, pos, edge_labels=edge_labels, font_color='black')

    plt.title(f"Shortest Distance from Emergency Unit {unit} to Incident Nodes with Edge Weights")
    plt.show()



@app.route('/result', methods=['POST'])
def result():
    incidents = []
    while True:
        description = request.form.get('description')
        if description.lower() == 'done':
            break
        incident_node = request.form.get('incident_node')
        incidents.append({"description": description, "node": incident_node})

    print("Received Incidents:", incidents)

    # Categorize incidents
    categorized_incidents = categorize_incidents(incidents)

    # Simulated emergency response unit locations
    emergency_units = ["1", "5", "9"]

    edges = []
    for i in range(1, 11):
        if i % 5 != 0:  # Connect horizontally
            edges.extend([(str(i), str(i + 1)), (str(i + 1), str(i))])
        if i <= 5:  # Connect vertically
            edges.extend([(str(i), str(i + 5)), (str(i + 5), str(i))])

    # Create the city graph with nodes and edges
    incident_nodes = [incident["node"] for incident in incidents]  # Extract incident nodes
    city_graph = nx.DiGraph()
    city_graph.add_nodes_from(incident_nodes)
    city_graph.add_edges_from(edges)

    # Assign random weights to the edges
    edge_weights = {edge: random.randint(1, 10) for edge in edges}
    nx.set_edge_attributes(city_graph, edge_weights, name='weight')
    shortest_distances = {}
    for unit in emergency_units:
        shortest_distances[unit] = {}
        for incident in incident_nodes:
            try:
                shortest_path = nx.shortest_path(city_graph, unit, incident, weight='weight')
                shortest_distances[unit][incident] = shortest_path
            except nx.NetworkXNoPath:
                shortest_distances[unit][incident] = "No path"

    # Simulated emergency resources
    resources = [
        Resource("Ambulance", 5),
        Resource("Fire Truck", 3),
        Resource("Police Car", 7)
    ]

    # Allocate resources based on categorized incidents
    allocated_resources = knapsack_allocation(resources, categorized_incidents)

    # Output the optimized resource allocation for incidents
    print("Allocated Resources:")
    for incident_type, incidents_list in allocated_resources.items():
        print(f"Incident Type: {incident_type}")
        for incident_resources in incidents_list:
            print(incident_resources)

    # Output shortest distances between emergency units and incident nodes
    print("\nShortest Distances:")
    for unit, distances in shortest_distances.items():
        print(f"From Emergency Unit {unit}:")
        for incident, shortest_path in distances.items():
            print(f"Shortest Path to Incident {incident}: {shortest_path}")

    # Visualize the graph showing connectivity between emergency units and incident nodes
    # visualize_graph(city_graph, shortest_distances)
    # Visualize shortest distance from each emergency unit to incident nodes separately

    for unit in emergency_units:
        visualize_graph_and_shortest_distances(city_graph, shortest_distances, unit)

    result_data = {
        "allocated_resources": allocated_resources,  # Modify this based on your output
        "shortest_distances": shortest_distances  # Modify this based on your output
    }

    return render_template('result.html', result=result_data)

if __name__ == '__main__':
    app.run(debug=True)