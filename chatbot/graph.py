from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from chatbot.tools import premium_filter

class State(TypedDict):
    messages: Annotated[list, add_messages]

def setup_graph(model):
    tools = [premium_filter]
    tool_node = ToolNode(tools)

    async def call_model(state: State):
        response = await model.ainvoke(state["messages"])
        return {"messages": [response]}

    def should_continue(state: State):
        last_message = state["messages"][-1]
        return "tools" if last_message.tool_calls else END

    memory = MemorySaver()
    workflow = StateGraph(State)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, ["tools", END])
    workflow.add_edge("tools", "agent")
    return workflow.compile(checkpointer=memory)

