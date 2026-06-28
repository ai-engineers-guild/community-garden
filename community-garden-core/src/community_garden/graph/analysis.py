from __future__ import annotations

from collections import defaultdict
from typing import Any

import networkx as nx

from community_garden.models import CommunityEvent


def build_interaction_graph(events: list[CommunityEvent]) -> nx.DiGraph:
    graph = nx.DiGraph()
    event_author = {e.event_id: e.actor.id for e in events if e.actor}
    for e in events:
        if not e.actor:
            continue
        actor = e.actor.id
        graph.add_node(actor, label=e.actor.display_name or actor)
        if e.relation.reply_to_event_id and e.relation.reply_to_event_id in event_author:
            target = event_author[e.relation.reply_to_event_id]
            if actor != target:
                current = graph.get_edge_data(actor, target, default={}).get("weight", 0)
                graph.add_edge(actor, target, weight=current + 1, kind="reply")
        for mention in e.relation.mentions:
            if mention != actor:
                current = graph.get_edge_data(actor, mention, default={}).get("weight", 0)
                graph.add_edge(actor, mention, weight=current + 1, kind="mention")
    return graph


def graph_metrics(graph: nx.DiGraph) -> dict[str, Any]:
    if graph.number_of_nodes() == 0:
        return {"nodes": 0, "edges": 0, "density": 0, "leaders": [], "bridges": [], "communities": []}
    undirected = graph.to_undirected()
    weighted_degree = sorted(graph.degree(weight="weight"), key=lambda x: x[1], reverse=True)
    try:
        betweenness = nx.betweenness_centrality(undirected, weight="weight")
    except Exception:
        betweenness = {n: 0 for n in graph.nodes}
    bridges = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:10]
    communities: list[list[str]] = []
    if undirected.number_of_edges() > 0 and undirected.number_of_nodes() > 1:
        try:
            from networkx.algorithms.community import louvain_communities
            communities = [sorted(list(c)) for c in louvain_communities(undirected, weight="weight", seed=42)]
        except Exception:
            communities = [sorted(list(c)) for c in nx.connected_components(undirected)]
    return {
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "density": round(nx.density(graph), 4),
        "leaders": weighted_degree[:10],
        "bridges": [(node, round(score, 4)) for node, score in bridges],
        "communities": communities,
    }


def export_graphml(graph: nx.DiGraph, path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(graph, path)
