from datetime import datetime
from modules.fraud_graph.graph_engine import get_graph_json, detect_clusters

def generate_case_packet(case_id: str, victim_name: str, summary_notes: str = ""):
    graph_data = get_graph_json()
    clusters = detect_clusters()

    packet = {
        "case_id": case_id,
        "generated_at": datetime.utcnow().isoformat(),
        "victim": victim_name,
        "summary": summary_notes or "Auto-generated fraud network intelligence packet.",
        "network_nodes": len(graph_data["nodes"]),
        "network_edges": len(graph_data["edges"]),
        "clusters_detected": len(clusters),
        "cluster_details": clusters,
        "graph": graph_data
    }
    return packet