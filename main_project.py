import networkx as nx
import matplotlib.pyplot as plt
import random

class Resource:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity
        self.remaining_capacity = capacity

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
        incident_node = incident["node"] 
        severity = get_incident_severity(incident)
        if rabin_karp(description, "fire"):
            categorized_incidents["Fire"].append({"description": description, "node": incident_node ,"severity": severity})
        elif rabin_karp(description, "medical") or rabin_karp(description, "ambulance"):
            categorized_incidents["Medical"].append({"description": description, "node": incident_node,"severity": severity})
        else:
            categorized_incidents["Other"].append({"description": description, "node": incident_node,"severity": severity})
    return categorized_incidents

def get_flow_distribution(city_graph, max_flow_dict, path):
    flow_distribution = {}
    for u, v in zip(path[:-1], path[1:]):
        flow_along_edge = max_flow_dict[u][v]
        capacity_of_edge = city_graph[u][v]['capacity']
        flow_distribution[(u, v)] = f"Flow = {flow_along_edge}/{capacity_of_edge}"
    return flow_distribution

def knapsack_allocation(resources, categorized_incidents):
    allocated_resources = {}

    for incident_type, incident_list in categorized_incidents.items():
        for categorized_incident in incident_list:
            incident_severity = get_incident_severity(categorized_incident)
            incident_resources = {resource.name: 0 for resource in resources}

            # Loop through resources and their capacities
            for i in range(len(resources)):
                resource = resources[i]
                remaining_capacity = resource.remaining_capacity

                # Define incident capacity based on severity and resource type
                incident_capacity = 0
                if incident_severity == "High":
                    if resource.name == "Fire Truck":
                        incident_capacity = min(3, remaining_capacity)
                    elif resource.name == "Ambulance":
                        incident_capacity = min(2, remaining_capacity)
                    elif resource.name == "Police Car":
                        incident_capacity = min(1, remaining_capacity)
                elif incident_severity == "Medium":
                    if resource.name == "Ambulance":
                        incident_capacity = min(3, remaining_capacity)
                    elif resource.name == "Police Car":
                        incident_capacity = min(2, remaining_capacity)
                    elif resource.name == "Fire Truck":
                        incident_capacity = min(0, remaining_capacity)
                else:
                    if resource.name == "Police Car":
                        incident_capacity = min(2, remaining_capacity)
                    elif resource.name == "Ambulance":
                        incident_capacity = min(1, remaining_capacity)
                    elif resource.name == "Fire Truck":
                        incident_capacity = min(0, remaining_capacity)

                # Allocate resources to the incident if there is capacity available
                if incident_capacity > 0:
                    incident_resources[resource.name] = incident_capacity
                    resources[i].remaining_capacity -= incident_capacity

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

def visualize_graph_and_shortest_distances(city_graph, categorized_incidents, shortest_distances, unit):
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(city_graph)

    # Create color map based on incident severity
    color_map = {
        "High": "red",
        "Medium": "orange",
        "Low": "yellow"
    }
    # Assign node colors based on incident severity
    node_colors = []
    for node in city_graph.nodes():
        node_severity = "Low"  # Default to Low severity if not found in categorized incidents
        for category, incidents in categorized_incidents.items():
            for incident in incidents:
                if incident["node"] == node:
                    node_severity = incident["severity"]
                    break
        node_colors.append(color_map[node_severity])
    # Draw the graph with nodes colored according to severity
    nx.draw(city_graph, pos, with_labels=True, node_size=500, node_color=node_colors, font_weight='bold')
    labels = nx.get_edge_attributes(city_graph, 'weight')
    nx.draw_networkx_edge_labels(city_graph, pos, edge_labels=labels, font_color='black')

    # Highlight shortest path edges from emergency unit to incident nodes
    for incident, shortest_path in shortest_distances[unit].items():
        if shortest_path != "No path":
            path_edges = [(shortest_path[i], shortest_path[i + 1]) for i in range(len(shortest_path) - 1)]
            nx.draw_networkx_edges(city_graph, pos, edgelist=path_edges, edge_color='green', width=2)
    plt.title(f"Graph with Shortest Distance from Emergency Unit {unit} to Incident Nodes & Severity-based Node Colors")
    plt.show()

def main():
    incidents = []
    while True:
        description = input("Enter incident description (or 'done' to finish): ")
        if description.lower() == 'done':
            break
        incident_node = input("Enter incident node number: ")
        incidents.append({"description": description, "node": incident_node})

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

    edge_capacities = {edge: random.randint(1, 5) for edge in edges}  # Assigning random capacities
    nx.set_edge_attributes(city_graph, edge_capacities, name='capacity')

        # Simulated emergency resources
    resources = [
        Resource("Ambulance", 8),
        Resource("Fire Truck", 7),
        Resource("Police Car", 7)
    ]

    # Allocate resources based on categorized incidents
    allocated_resources = knapsack_allocation(resources, categorized_incidents)

    shortest_distances = {}
    for unit in emergency_units:
        shortest_distances[unit] = {}
        for incident in incident_nodes:
            try:
                shortest_path = nx.shortest_path(city_graph, unit, incident, weight='weight')
                shortest_distances[unit][incident] = shortest_path
            except nx.NetworkXNoPath:
                shortest_distances[unit][incident] = "No path"

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

    max_flows = {}
    for unit in emergency_units:
        max_flows[unit] = {}
        for incident in incident_nodes:
            try:
                max_flow_value, max_flow_dict = nx.maximum_flow(city_graph, unit, incident, capacity='capacity')
                max_flows[unit][incident] = {
                    "max_flow_value": max_flow_value,
                    "max_flow_dict": max_flow_dict
                }
            except nx.NetworkXError:
                max_flows[unit][incident] = "No path"

    # Outputting the maximum flow information with corrected flow distribution along the paths
    print("\nMax Flows Information:")
    for unit, flows in max_flows.items():
        print(f"From Emergency Unit {unit}:")
        for incident, flow_info in flows.items():
            if flow_info == "No path":
                print(f"No path from Emergency Unit {unit} to Incident {incident}")
            else:
                max_flow_value = flow_info["max_flow_value"]
                max_flow_dict = flow_info["max_flow_dict"]
                print(f"Max Flow from Emergency Unit {unit} to Incident {incident}: {max_flow_value}")

                # Displaying the path of the maximum flow
                path = nx.shortest_path(city_graph, source=unit, target=incident)
                print(f"Path taken: {path}")

                # Displaying the corrected flow distribution along the path
                flow_distribution = get_flow_distribution(city_graph, max_flow_dict, path)
                print("Flow Distribution along the path:")
                for edge, flow_info in flow_distribution.items():
                    print(f"Edge {edge}: {flow_info}")
                print() 

    # Visualize shortest distance from each emergency unit to incident nodes separately
    for unit in emergency_units:
        visualize_graph_and_shortest_distances(city_graph, categorized_incidents, shortest_distances, unit)

if __name__ == "__main__":
    main()
