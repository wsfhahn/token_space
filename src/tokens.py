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


def build_1d_graph(client: OpenAI, model: str, depth: int, base: str) -> TokenNode:
    root = TokenNode(base)
    nodes: list[TokenNode] = [root]

    for _ in range(depth):
        prev = nodes[-1]
        try:
            completion = client.completions.create(
                model=model,
                prompt=prev.token,
                max_tokens=1
            ).choices[0].text
        except Exception as e:
            raise Exception(f"Failed to get completion: {e}") from e
        new = TokenNode(prev.token + completion)
        prev.add_target(new)
        nodes.append(new)
    
    return root


def get_random_branch(root: TokenNode) -> list[TokenNode]: # type: ignore
    out = [root]
    current = root
    targets = root.get_targets()
    candidates = targets

    while candidates:
        


def complete_from_random_node(client: OpenAI, model: str, depth: int)