import networkx as nx

G = nx.Graph()

def add_case_data(case_id: str, numbers: list[str], accounts: list[str], victim: str = None):
    if victim:
        G.add_node(victim, type="victim")
    for num in numbers:
        G.add_node(num, type="phone")
        if victim:
            G.add_edge(victim, num, relation="contacted_by")
    for acc in accounts:
        G.add_node(acc, type="account")
        for num in numbers:
            G.add_edge(num, acc, relation="linked_to")

    return {"case_id": case_id, "nodes_added": len(numbers) + len(accounts) + (1 if victim else 0)}

def get_graph_json():
    nodes = [{"id": n, "type": G.nodes[n].get("type", "unknown")} for n in G.nodes]
    edges = [{"source": u, "target": v, "relation": G.edges[u, v].get("relation", "")} for u, v in G.edges]
    return {"nodes": nodes, "edges": edges}

def detect_clusters():
    communities = nx.community.greedy_modularity_communities(G)
    return [list(c) for c in communities]