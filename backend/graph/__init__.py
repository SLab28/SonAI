"""SonAI Graph State Manager — DAG for node placement and execution."""
from __future__ import annotations
import uuid
from typing import Any, Optional
from collections import defaultdict, deque


class GraphState:
    """In-memory DAG of nodes and edges, with topological execution order."""

    def __init__(self):
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, str]] = []
        self._adj: dict[str, list[str]] = defaultdict(list)

    def place_node(
        self,
        node_type: str,
        x: float = 0,
        y: float = 0,
        params: Optional[dict] = None,
    ) -> str:
        node_id = str(uuid.uuid4())
        self.nodes[node_id] = {
            "node_id": node_id,
            "node_type": node_type,
            "x": x,
            "y": y,
            "params": params or {},
            "result": None,
        }
        return node_id

    def connect_nodes(
        self,
        source_id: str,
        source_port: str,
        target_id: str,
        target_port: str,
    ) -> dict:
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("Source or target node not found in graph")
        edge = {
            "source_id": source_id,
            "source_port": source_port,
            "target_id": target_id,
            "target_port": target_port,
        }
        self.edges.append(edge)
        self._adj[source_id].append(target_id)
        # Check for cycles
        if self._has_cycle():
            self.edges.pop()
            self._adj[source_id].remove(target_id)
            raise ValueError("Connection would create a cycle")
        return edge

    def _has_cycle(self) -> bool:
        visited = set()
        in_stack = set()
        for node in self.nodes:
            if node not in visited:
                if self._dfs_cycle(node, visited, in_stack):
                    return True
        return False

    def _dfs_cycle(self, node: str, visited: set, in_stack: set) -> bool:
        visited.add(node)
        in_stack.add(node)
        for neighbor in self._adj.get(node, []):
            if neighbor not in visited:
                if self._dfs_cycle(neighbor, visited, in_stack):
                    return True
            elif neighbor in in_stack:
                return True
        in_stack.discard(node)
        return False

    def topo_sort(self) -> list[str]:
        in_degree: dict[str, int] = {n: 0 for n in self.nodes}
        for src, targets in self._adj.items():
            for t in targets:
                in_degree[t] = in_degree.get(t, 0) + 1
        queue = deque(n for n, d in in_degree.items() if d == 0)
        order = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in self._adj.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        return order

    def get_state(self) -> dict:
        return {
            "nodes": list(self.nodes.values()),
            "edges": self.edges,
        }

    def set_node_result(self, node_id: str, result: dict):
        if node_id in self.nodes:
            self.nodes[node_id]["result"] = result

    def reset(self):
        self.nodes.clear()
        self.edges.clear()
        self._adj.clear()


# Singleton graph
graph = GraphState()
