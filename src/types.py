from dataclasses import dataclass
from string import ascii_letters, digits
from random import choice


def create_uuid(len: int) -> str:
    chars = ascii_letters + digits
    string = "".join(choice(chars) for _ in range(len))
    return string


class TokenNode:
    def __init__(self, token: str, targets: list["TokenNode"] | None = None):
        self.token = token
        self.uuid = create_uuid(32)
        self.targets = targets if targets is not None else []
    
    def __repr__(self) -> str:
        return self.token
    
    def add_target(self, node: "TokenNode") -> None:
        self.targets.append(node)
    
    def add_targets(self, nodes: list["TokenNode"]) -> None:
        self.targets.extend(nodes)
    
    def get_targets(self) -> list["TokenNode"]:
        return self.targets


class TokenNodeQueue:
    def __init__(self, nodes: list[TokenNode] | None = None):
        self.nodes = nodes if nodes is not None else []
    
    def add_node(self, node: TokenNode) -> None:
        self.nodes.append(node)
    
    def add_nodes(self, nodes: list[TokenNode]) -> None:
        self.nodes.extend(nodes)
    
    def pop_left(self) -> TokenNode:
        node = self.nodes.pop(0)
        return node

    def pop_right(self) -> TokenNode:
        node = self.nodes.pop(-1)
        return node