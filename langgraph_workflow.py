"""
Write LangGraph workflow
- start with 2 inputs (a and b)
- node 1 - do the addition
- node 2 - do the multiplication
- node 3 - collect the value sum as well as the multiplication, print it
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END

class MathState(TypedDict):
    a: int
    b: int
    sum: int
    product: int

def add_node(state: MathState):
    result = state["a"] + state["b"]
    return {"sum": result}

def multiply_node(state: MathState):
    result = state["a"] * state["b"]
    return {"product": result}

def collect_node(state: MathState):
    print(f"Sum = {state['sum']}")
    print(f"Product = {state['product']}")
    return {}

# create the graph state
graph = StateGraph(MathState)

# Add nodes
graph.add_node("add", add_node)
graph.add_node("multiply", multiply_node)
graph.add_node("collect", collect_node)

# define the order
graph.set_entry_point("add")
graph.add_edge("add", "multiply")
graph.add_edge("multiply", "collect")
graph.add_edge("collect", END)

# compile the graph
app = graph.compile()


# running the workflow
input_data = {"a": 4, "b": 5}

app.invoke(input_data)
