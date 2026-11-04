"""
ExposureLens Interactive Exposure Graph Engine.

Builds a NetworkX directed graph from verified database records:
Requester (User) -> Exposure Event (EXP-xxxx) -> Resource -> Owner/Victim (User) -> Tenant

Generates interactive Plotly visualizations and calculates security graph metrics.
"""

from typing import Any, Dict, List, Optional
import networkx as nx
import plotly.graph_objects as go

from backend.database import SessionLocal
from backend.models import Document, ExposureRecord, Order, Tenant, User


def build_exposure_graph(db_session=None) -> nx.DiGraph:
    """Construct a directed NetworkX graph representing verified BOLA exposure paths."""
    owns_session = False
    if db_session is None:
        db = SessionLocal()
        owns_session = True
    else:
        db = db_session

    G = nx.DiGraph()

    try:
        exposures = db.query(ExposureRecord).all()
        users = {u.id: u for u in db.query(User).all()}
        tenants = {t.id: t for t in db.query(Tenant).all()}

        for exp in exposures:
            req_u = users.get(exp.requester_user_id)
            vic_u = users.get(exp.victim_user_id)
            req_t = tenants.get(exp.requester_tenant_id)
            vic_t = tenants.get(exp.resource_tenant_id)

            req_label = f"User {exp.requester_user_id} ({req_u.username if req_u else '?'})"
            vic_label = f"User {exp.victim_user_id} ({vic_u.username if vic_u else '?'})"
            res_label = f"{exp.resource_type.upper()} #{exp.resource_id}"
            exp_label = exp.exposure_id

            req_t_name = f"Tenant: {req_t.name if req_t else 'Unknown'}"
            vic_t_name = f"Tenant: {vic_t.name if vic_t else 'Unknown'}"

            # 1. Add Nodes
            # Requester Node
            G.add_node(
                req_label,
                node_type="requester",
                user_id=exp.requester_user_id,
                tenant=req_t_name,
                color="#EF4444",  # Red
                size=24,
                title=f"Requester / Attacker: {req_label}<br>Tenant: {req_t_name}"
            )

            # Exposure Event Node
            severity_colors = {
                "CRITICAL": "#DC2626",
                "HIGH": "#F97316",
                "MEDIUM": "#FBBF24",
                "LOW": "#10B981"
            }
            exp_color = severity_colors.get(exp.risk_severity, "#8B5CF6")
            G.add_node(
                exp_label,
                node_type="exposure",
                exposure_id=exp.exposure_id,
                risk_score=exp.risk_score,
                risk_severity=exp.risk_severity,
                is_cross_tenant=exp.is_cross_tenant,
                color=exp_color,
                size=18,
                title=(
                    f"Exposure: {exp.exposure_id}<br>"
                    f"Risk: {exp.risk_score} ({exp.risk_severity})<br>"
                    f"Cross-Tenant: {exp.is_cross_tenant}<br>"
                    f"Endpoint: {exp.endpoint}"
                )
            )

            # Resource Node
            G.add_node(
                res_label,
                node_type="resource",
                resource_type=exp.resource_type,
                resource_id=exp.resource_id,
                sensitivity=exp.sensitivity_level,
                color="#3B82F6",  # Blue
                size=20,
                title=f"Resource: {res_label}<br>Sensitivity: {exp.sensitivity_level}"
            )

            # Victim Node
            G.add_node(
                vic_label,
                node_type="victim",
                user_id=exp.victim_user_id,
                tenant=vic_t_name,
                color="#8B5CF6",  # Purple
                size=22,
                title=f"Victim / Owner: {vic_label}<br>Tenant: {vic_t_name}"
            )

            # Tenant Nodes
            G.add_node(
                req_t_name,
                node_type="tenant",
                color="#0D9488",  # Teal
                size=26,
                title=f"Tenant Domain: {req_t_name}"
            )
            G.add_node(
                vic_t_name,
                node_type="tenant",
                color="#0D9488",
                size=26,
                title=f"Tenant Domain: {vic_t_name}"
            )

            # 2. Add Directed Edges
            # Requester -> Exposure Event
            G.add_edge(req_label, exp_label, relation="triggered", cross_tenant=exp.is_cross_tenant)
            # Exposure Event -> Resource
            G.add_edge(exp_label, res_label, relation="exposed_resource", cross_tenant=exp.is_cross_tenant)
            # Resource -> Victim
            G.add_edge(res_label, vic_label, relation="owned_by", cross_tenant=False)
            # Users to Tenants
            G.add_edge(req_label, req_t_name, relation="belongs_to", cross_tenant=False)
            G.add_edge(vic_label, vic_t_name, relation="belongs_to", cross_tenant=False)

        return G
    finally:
        if owns_session:
            db.close()


def compute_graph_metrics(G: nx.DiGraph) -> Dict[str, Any]:
    """Compute security metrics from the exposure graph."""
    if len(G) == 0:
        return {
            "total_nodes": 0,
            "total_edges": 0,
            "most_active_requesters": [],
            "most_targeted_victims": [],
            "most_exposed_resources": [],
            "cross_tenant_paths_count": 0
        }

    requester_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "requester"]
    victim_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "victim"]
    resource_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "resource"]
    exposure_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "exposure"]

    requester_activity = sorted(
        [(n, G.out_degree(n)) for n in requester_nodes],
        key=lambda x: x[1],
        reverse=True
    )

    victim_exposure = sorted(
        [(n, G.in_degree(n)) for n in victim_nodes],
        key=lambda x: x[1],
        reverse=True
    )

    resource_exposure = sorted(
        [(n, G.in_degree(n)) for n in resource_nodes],
        key=lambda x: x[1],
        reverse=True
    )

    cross_tenant_edges = sum(1 for _, _, d in G.edges(data=True) if d.get("cross_tenant"))

    return {
        "total_nodes": len(G.nodes()),
        "total_edges": len(G.edges()),
        "requester_nodes_count": len(requester_nodes),
        "victim_nodes_count": len(victim_nodes),
        "resource_nodes_count": len(resource_nodes),
        "exposure_nodes_count": len(exposure_nodes),
        "most_active_requesters": requester_activity,
        "most_targeted_victims": victim_exposure,
        "most_exposed_resources": resource_exposure,
        "cross_tenant_paths_count": cross_tenant_edges
    }


def create_plotly_exposure_graph(G: nx.DiGraph, title: str = "BOLA Exposure Relationship Graph") -> go.Figure:
    """Generate an interactive Plotly graph figure from the NetworkX exposure graph."""
    if len(G) == 0:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text="Exposure Graph (No Data)"),
            annotations=[dict(text="No exposure events recorded", showarrow=False)]
        )
        return fig

    # Compute node positions using deterministic spring layout
    pos = nx.spring_layout(G, k=0.9, iterations=60, seed=42)

    # Prepare edge traces
    edge_x = []
    edge_y = []

    for edge in G.edges(data=True):
        u, v, data = edge
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1.2, color="#94A3B8"),
        hoverinfo="none",
        mode="lines"
    )

    # Prepare node traces
    node_x = []
    node_y = []
    node_color = []
    node_size = []
    node_text = []
    node_hover = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        data = G.nodes[node]
        node_color.append(data.get("color", "#64748B"))
        node_size.append(data.get("size", 20))
        node_text.append(node)
        node_hover.append(data.get("title", node))

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="top center",
        textfont=dict(size=10, color="#1E293B"),
        hoverinfo="text",
        hovertext=node_hover,
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            line=dict(width=2, color="#FFFFFF")
        )
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(text=title, font=dict(size=18)),
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=10, r=10, t=50),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="#F8FAFC",
            paper_bgcolor="#F8FAFC",
            height=650
        )
    )

    return fig


if __name__ == "__main__":
    G = build_exposure_graph()
    fig = create_plotly_exposure_graph(G)
    print("\n=== Exposure Graph Plotly Figure Created Successfully ===")
    print("Traces:", len(fig.data))
    print("Layout Title:", fig.layout.title.text)
