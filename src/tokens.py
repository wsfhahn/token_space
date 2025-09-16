from src import TokenNode, TokenNodeQueue
from openai import OpenAI
from wordsegment import load, segment



def build_token_graph(client: OpenAI, model: str, depth: int, completions_per_node: int, max_retries: int, base: str, use_wordseg: bool) -> TokenNode:
    """Build a token graph, completing off of a base string."""

    if use_wordseg:
        load()

    root = TokenNode(base)
    frontier: list[TokenNode] = [root]

    for i in range(depth):
        next_frontier: list[TokenNode] = []
        for node in frontier:
            r = 0
            curr_scope: list[TokenNode] = []
            while (len(curr_scope) < completions_per_node) and (r < max_retries):
                try:
                    completion = client.completions.create(
                        model=model,
                        prompt=node.token,
                        max_tokens=1
                    ).choices[0].text
                except Exception as e:
                    raise Exception(f"Could not create completion :{e}") from e
                if use_wordseg:
                    new_node = TokenNode(" ".join(segment(node.token + completion)))
                else:
                    new_node = TokenNode(node.token + completion)
                if new_node.token not in [x.token for x in curr_scope]:
                    node.add_target(new_node)
                    curr_scope.append(new_node)
                r += 1
            next_frontier.extend(curr_scope)
        frontier = next_frontier
    return root


if __name__ == "__main__":
    from src.viz_v2 import export_sigma_force_graph_html

    client = OpenAI(
        base_url="http://100.95.73.15:1234/v1",
        api_key = "not-needed"
    )
    model = "qwen3-30b-2507"
    depth = 3
    completions_per_node = 3
    max_retries = 20
    base = "Once upon a time in a little town called"
    use_wordseg = True

    root = build_token_graph(client,
                             model,
                             depth,
                             completions_per_node,
                             max_retries,
                             base,
                             use_wordseg)
    
    export_sigma_force_graph_html(root, "test.html")