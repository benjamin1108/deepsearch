# Lazy import to avoid initialization issues
def get_graph():
    from agent.graph import graph
    return graph

__all__ = ["get_graph"]
