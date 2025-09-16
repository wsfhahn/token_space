from src import TokenNode


def save_graph_json(root: "TokenNode", filepath: str, *, indent: int = 2) -> None:
    """
    Save the graph reachable from `root` to a JSON file.

    JSON schema:
    {
      "root": "<root_uuid>",
      "nodes": {
        "<uuid>": {
          "token": "<token_text>",
          "targets": ["<uuid>", ...]
        },
        ...
      }
    }
    """
    import json
    from collections import deque
    from typing import Deque, Dict, List, TypedDict

    class JsonNode(TypedDict):
        token: str
        targets: List[str]

    nodes: Dict[str, JsonNode] = {}
    visited: set[str] = set()
    q: Deque["TokenNode"] = deque([root])

    while q:
        node = q.popleft()
        uid = node.uuid
        if uid in visited:
            continue
        visited.add(uid)

        target_ids: List[str] = [t.uuid for t in node.get_targets()]
        nodes[uid] = {"token": node.token, "targets": target_ids}

        for t in node.get_targets():
            if t.uuid not in visited:
                q.append(t)

    graph_obj: Dict[str, object] = {"root": root.uuid, "nodes": nodes}

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(graph_obj, f, ensure_ascii=False, indent=indent)


def load_graph_json(filepath: str) -> "TokenNode":
    """
    Load a graph from a JSON file (schema produced by `save_graph_json`) and
    return the root TokenNode.
    """
    import json
    from typing import TypedDict, Dict, List, cast

    class JsonNode(TypedDict):
        token: str
        targets: List[str]

    class GraphObj(TypedDict):
        root: str
        nodes: Dict[str, JsonNode]

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    graph = cast(GraphObj, data)

    if "root" not in graph or "nodes" not in graph:
        raise ValueError("Invalid graph JSON: missing 'root' or 'nodes' key")

    nodes_data = graph["nodes"]
    root_id = graph["root"]

    # First pass: create TokenNode objects and fix their UUIDs
    id_to_node: Dict[str, TokenNode] = {}
    for uid, node_data in nodes_data.items():
        token = node_data["token"]
        node = TokenNode(token)     # uuid is auto-generated...
        node.uuid = uid             # ...overwrite to match JSON
        id_to_node[uid] = node

    if root_id not in id_to_node:
        raise ValueError(f"Root id '{root_id}' not found in nodes")

    # Second pass: connect edges
    for uid, node_data in nodes_data.items():
        node = id_to_node[uid]
        target_nodes: List[TokenNode] = []
        for tid in node_data["targets"]:
            if tid not in id_to_node:
                raise ValueError(f"Target id '{tid}' referenced by '{uid}' not found in nodes")
            target_nodes.append(id_to_node[tid])
        node.targets = target_nodes  # assign edges

    return id_to_node[root_id]