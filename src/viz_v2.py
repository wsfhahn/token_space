#!/usr/bin/env python3
from __future__ import annotations

import json
import uuid
from collections import deque
from typing import Deque, Dict, List, Optional, Set

from src import TokenNode


def export_sigma_force_graph_html(
    root: "TokenNode",
    out_html: str,
    *,
    title: str = "Token Graph",
    base_node_size: float = 5.0
) -> None:
    """
    Export the graph reachable from `root` as a self-contained HTML page that
    renders a WebGL force-directed visualization using Sigma.js + Graphology.
    - Animates by applying small ForceAtlas2 steps each animation frame.
    - Shows hover tooltips using container pixel coords (no dragging/zooming required).
    - Uses UMD <script> tags (no import maps needed).
    """

    # Collect nodes/edges via BFS
    nodes: List[Dict[str, object]] = []
    edges: List[Dict[str, object]] = []
    seen: Set[str] = set()
    degree: Dict[str, int] = {}

    q: Deque["TokenNode"] = deque([root])

    while q:
        node = q.popleft()
        if node.uuid in seen:
            continue
        seen.add(node.uuid)

        nodes.append(
            {
                "id": node.uuid,
                "label": node.token,
                # initial positions are randomized in JS; keep placeholders here
                "x": 0.0,
                "y": 0.0,
                "size": float(base_node_size),
                "color": "#60a5fa",
            }
        )

        for tgt in node.get_targets():
            edges.append(
                {
                    "key": f"{node.uuid}->{tgt.uuid}",
                    "source": node.uuid,
                    "target": tgt.uuid,
                }
            )
            degree[node.uuid] = degree.get(node.uuid, 0) + 1
            degree[tgt.uuid] = degree.get(tgt.uuid, 0) + 1
            if tgt.uuid not in seen:
                q.append(tgt)

    data = {"nodes": nodes, "edges": edges, "root": root.uuid}
    data_json = json.dumps(data, ensure_ascii=False)

    # Plain string template (avoid f-strings to prevent { } interpolation issues)
    TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>%%TITLE%%</title>
  <style>
    html, body, #container { height: 100%; margin: 0; background: #0b1020; }
    #container { position: relative; }
    #legend {
      position: absolute; right: 12px; top: 12px;
      background: rgba(20,25,45,0.8); color: #cbd5e1; padding: 8px 10px; border-radius: 8px;
      font: 12px/1.4 system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    }
  </style>
  <!-- UMD builds via <script> tags (globals: Sigma, graphology, graphologyLibrary) -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/sigma.js/3.0.0/sigma.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/graphology/0.26.0/graphology.umd.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/graphology-library@0.8.0/dist/graphology-library.min.js"></script>
</head>
<body>
  <div id="container"></div>
  <div id="legend">💡 Drag to pan · Scroll to zoom · Nodes: %%NODE_COUNT%%</div>

  <script>
    // Graph data injected from Python:
    const DATA = %%DATA_JSON%%;

    // Build graphology graph (directed)
    const graph = new graphology.Graph({ type: 'directed', multi: false, allowSelfLoops: true });

    // Seed positions around a circle (FA2 needs nonzero x/y)
    const TWO_PI = Math.PI * 2;
    const N = DATA.nodes.length || 1;
    DATA.nodes.forEach((nObj, i) => {
      const a = (i / N) * TWO_PI;
      const r = 1 + Math.random() * 0.5;
      graph.addNode(nObj.id, {
        label: nObj.label,
        x: Math.cos(a) * r,
        y: Math.sin(a) * r,
        size: nObj.size,
        color: nObj.color
      });
    });

    DATA.edges.forEach((e, idx) => {
      const key = e.key || ('e' + idx);
      if (!graph.hasEdge(key)) graph.addEdgeWithKey(key, e.source, e.target);
    });

    // Create Sigma renderer (labels off; hover tooltip instead)
    const container = document.getElementById('container');
    const renderer = new Sigma(graph, container, {
      renderLabels: false,
      enableEdgeHoverEvents: true,
      labelDensity: 0.07,
      zIndex: true,
      defaultEdgeType: "line",
      defaultEdgeColor: "#64748b",
      defaultEdgeSize: 0.5
    });

    // Animate: apply tiny FA2 steps every frame (main-thread "poor man's worker")
    
    const fa2Settings = graphologyLibrary.layoutForceAtlas2.inferSettings(graph);

    function stepFA2() {
      // one or few iterations per frame keeps it lively without freezing
      graphologyLibrary.layoutForceAtlas2.assign(graph, { iterations: 5, settings: fa2Settings });
      requestAnimationFrame(stepFA2);
    }
    requestAnimationFrame(stepFA2);

    // Hover tooltip using container pixel coords (event.x/event.y)
    const tooltip = document.createElement('div');
    Object.assign(tooltip.style, {
      position: 'absolute',
      pointerEvents: 'none',
      padding: '4px 6px',
      borderRadius: '6px',
      background: 'rgba(20,25,45,0.9)',
      color: '#e2e8f0',
      font: '12px system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
      transform: 'translate(-50%, -140%)',
      whiteSpace: 'nowrap',
      display: 'none'
    });
    container.appendChild(tooltip);

    let hoveredNode = null;

    function showTooltip(nodeId, x, y) {
      tooltip.textContent = graph.getNodeAttribute(nodeId, 'label') || '';
      tooltip.style.left = x + 'px';
      tooltip.style.top  = y + 'px';
      tooltip.style.display = 'block';
    }

    renderer.on('enterNode', ({ node, event }) => {
      hoveredNode = node;
      showTooltip(node, event.x, event.y);
    });

    renderer.on('leaveNode', () => {
      hoveredNode = null;
      tooltip.style.display = 'none';
    });

    renderer.on('mousemove', ({ event }) => {
      if (hoveredNode) showTooltip(hoveredNode, event.x, event.y);
    });

    // Fit camera
    renderer.getCamera().animatedReset({ duration: 600 });
  </script>
</body>
</html>
"""

    html_doc = (
        TEMPLATE.replace("%%TITLE%%", title)
        .replace("%%NODE_COUNT%%", str(len(nodes)))
        .replace("%%DATA_JSON%%", data_json)
    )

    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html_doc)


# --- Example usage when run as a script ---
if __name__ == "__main__":
    # Build a small sample graph
    root = TokenNode("Root")
    a = TokenNode("Alpha")
    b = TokenNode("Beta")
    c = TokenNode("Gamma")
    d = TokenNode("Delta")
    e = TokenNode("Epsilon")
    f = TokenNode("Phi")
    g = TokenNode("Omega")

    root.add_targets([a, b, c])
    a.add_targets([d, e])
    b.add_target(e)
    c.add_targets([f, g])
    e.add_target(g)
    d.add_target(f)

    export_sigma_force_graph_html(root, "graph.html", title="Token Graph (Animated)", base_node_size=12.0)
    print("Wrote graph.html — open it in a browser.")
