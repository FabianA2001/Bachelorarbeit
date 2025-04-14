class Node:
    def __init__(self, name: str, pos: tuple[int, int], degree: int = 0) -> None:
        self.name = name
        self.pos = pos
        self.degree = degree

    def __str__(self) -> str:
        return f"{self.name} ({self.pos[0]}, {self.pos[1]})"

    def __repr__(self) -> str:
        return f"Node({self.name}, {self.pos})"
